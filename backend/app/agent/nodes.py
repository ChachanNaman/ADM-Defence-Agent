"""LangGraph node functions (PRD architecture diagram, section 4)."""

import json
from typing import Literal

from app.agent import tools
from app.agent.drafting import draft_dispute_letter, draft_pay_auth, escalate_to_human
from app.agent.llm import complete_json
from app.agent.state import AgentState
from app.config import (
    ESCALATE_ABOVE_AMOUNT,
    ESCALATE_BELOW_CONFIDENCE,
    ESCALATE_BELOW_RETRIEVAL_SCORE,
)
from app.rag.store import retrieve_fare_rule

_ANALYSIS_SYSTEM = """You are an ADM (Agency Debit Memo) defense analyst for a travel \
consolidator's back office. You will be given an airline's ADM claim, the actual PNR \
booking record, excerpts retrieved from that airline's published fare rules, and the \
results of deterministic verification checks (advance-purchase math, booking-class \
match, recomputed taxes).

Decide whether the ADM's claim is actually correct. Follow this rubric strictly:
- Recommend "DISPUTE" only when your evidence CONTRADICTS the ADM's claim — e.g. the \
ADM cites a rule category that isn't filed for this fare basis, cites a requirement \
that the verification results show is actually satisfied, or asserts a fact about the \
ticket that the PNR record contradicts.
- Recommend "PAY" when the ADM's claim is specific, correctly cites the fare basis, and \
you find NO contradicting evidence anywhere in the retrieved rules or verification \
results — including when the retrieved rules directly CONFIRM the ADM's claim is correct.
- Recommend "ESCALATE" when the retrieved rules are generic/insufficient to adjudicate \
this specific claim, the evidence is genuinely conflicting, or you are not confident \
either way.

CRITICAL — check directionality before you answer: a retrieved rule passage is evidence \
FOR "DISPUTE" only if, applied to this booking, it shows the ADM is WRONG. If the same \
passage instead shows the ADM's claim holds (e.g. it confirms the fare basis really \
does require what the ADM says, and this booking doesn't meet that requirement), that is \
evidence FOR "PAY", not "DISPUTE" — finding *a* relevant rule is not itself grounds to \
dispute; only a rule that contradicts the claim is. Before finalizing, re-read your own \
"reasoning" and confirm your "decision" is the side your reasoning actually argues for — \
if your reasoning concludes the ADM's claim is supported/correct, the decision must be \
"PAY", never "DISPUTE".

"confidence" (0.0-1.0) must reflect how strong your evidence actually is. Report confidence \
>= 0.85 when you found a specific, quotable rule passage or verification result that \
directly supports your decision — this includes cases where the rule text itself states \
that a fact (e.g. completed travel dates) is only verifiable in the airline's own systems \
and instructs you to treat the airline's claim as accurate absent a documented exception: \
that instruction, applied with no contradicting PNR remark, IS a specific, quotable basis \
for confident PAY, not a reason to hedge below 0.70. Reserve confidence below 0.70 for \
cases where the retrieved rules are actually silent, generic, or conflicting on the \
specific question asked.

Respond with ONLY a single JSON object and nothing else:
{"decision": "DISPUTE" | "PAY" | "ESCALATE", "confidence": 0.0-1.0, \
"citation": "short quote or category reference from the retrieved rule text, or empty string", \
"reasoning": "2-4 sentences, factual, referencing the specific evidence used"}"""


def parse_adm(state: AgentState) -> dict:
    adm = tools.get_adm(state["adm_id"])
    if adm is None:
        raise ValueError(f"ADM {state['adm_id']} not found")
    return {
        "adm": adm,
        "trace": [
            {
                "step": "parse_adm",
                "message": f"Parsed ADM {adm['adm_id']}: {adm['airline_code']} reason "
                f"{adm['reason_code']}, ${adm['amount_claimed']:.2f} claimed, "
                f"deadline {adm['dispute_deadline']}.",
                "data": adm,
            }
        ],
    }


def lookup_booking(state: AgentState) -> dict:
    pnr = tools.lookup_booking(state["adm"]["ticket_number"])
    if pnr is None:
        message = f"No PNR found for ticket {state['adm']['ticket_number']}."
    else:
        message = (
            f"Pulled PNR {pnr['pnr_id']}: {pnr['origin']}-{pnr['destination']}, "
            f"fare basis {pnr['fare_basis_code']}, class {pnr['booking_class']}, "
            f"booked {pnr['booking_date']} for departure {pnr['departure_date']}."
        )
    return {
        "pnr": pnr,
        "trace": [{"step": "lookup_booking", "message": message, "data": pnr or {}}],
    }


def retrieve_rule(state: AgentState) -> dict:
    adm, pnr = state["adm"], state.get("pnr")
    fare_basis = pnr["fare_basis_code"] if pnr else None
    chunks = retrieve_fare_rule(
        airline_code=adm["airline_code"],
        query_text=adm["reason_text"],
        fare_basis=fare_basis,
        k=3,
    )
    top_score = chunks[0].score if chunks else 0.0
    serialized = [
        {
            "heading": c.heading,
            "source": c.source,
            "fare_basis": c.fare_basis,
            "score": round(c.score, 4),
            "text": c.text,
        }
        for c in chunks
    ]
    if chunks:
        message = (
            f"RAG retrieval over {adm['airline_code']} fare rule corpus, filtered to "
            f"airline_code={adm['airline_code']}. Top match: \"{chunks[0].heading}\" "
            f"(similarity {top_score:.2f})."
        )
    else:
        message = f"RAG retrieval returned no chunks for airline {adm['airline_code']}."
    return {
        "rule_chunks": serialized,
        "retrieval_score": top_score,
        "trace": [{"step": "retrieve_rule", "message": message, "data": {"top_score": top_score}}],
    }


def verify_calculation(state: AgentState) -> dict:
    pnr = state.get("pnr")
    if pnr is None:
        verification = {
            "advance_purchase": {"applicable": False},
            "booking_class": {"applicable": False},
            "tax_calculation": {"applicable": False},
        }
        message = "No PNR on file — verification checks skipped."
    else:
        ap = tools.check_advance_purchase(pnr)
        bc = tools.check_booking_class_match(pnr)
        tax = tools.verify_tax_calculation(pnr)
        verification = {
            "advance_purchase": ap,
            "booking_class": bc,
            "tax_calculation": tax,
        }
        bits = []
        if ap.get("applicable"):
            bits.append(
                f"advance purchase {'satisfied' if ap['satisfied'] else 'VIOLATED'} "
                f"({ap['actual_days']}d actual vs {ap['required_days']}d required)"
            )
        if bc.get("match") is not None:
            bits.append(
                f"booking class {'matches' if bc['match'] else 'MISMATCHES'} fare basis "
                f"({bc['ticketed_class']} vs {bc['fare_basis_class']})"
            )
        if tax.get("applicable") and tax.get("under_collected"):
            bits.append(f"tax shortfall of ${tax['shortfall']:.2f} found")
        elif tax.get("applicable"):
            bits.append("taxes on file match recomputed amount")
        message = "Verification: " + "; ".join(bits) if bits else "No verification checks applicable."
    return {
        "verification": verification,
        "trace": [{"step": "verify_calculation", "message": message, "data": verification}],
    }


def analyze(state: AgentState) -> dict:
    adm, pnr = state["adm"], state.get("pnr")
    rule_chunks = state.get("rule_chunks", [])
    retrieval_score = state.get("retrieval_score", 0.0)
    verification = state.get("verification", {})

    if pnr is None:
        analysis = {"decision": "ESCALATE", "confidence": 0.0, "citation": "", "reasoning": "No PNR on file for this ticket number."}
        escalation_reason = "booking record not found"
    else:
        user_payload = json.dumps(
            {
                "adm": adm,
                "pnr": pnr,
                "retrieved_fare_rules": [
                    {"heading": c["heading"], "text": c["text"]} for c in rule_chunks[:3]
                ],
                "verification_results": verification,
            },
            indent=2,
            default=str,
        )
        analysis = complete_json(_ANALYSIS_SYSTEM, user_payload)
        escalation_reason = None

    if analysis.get("_parse_error"):
        decision, confidence = "ESCALATE", 0.0
        raw = analysis.get("_raw", "")
        if "quota exhausted" in raw or "RateLimitError" in raw or "call failed after" in raw:
            escalation_reason = "LLM temporarily unavailable (upstream rate limit)"
            analysis["reasoning"] = (
                "The model provider returned a rate-limit error and no analysis could be "
                "produced; routed to human review rather than guessing. "
                f"Upstream detail: {raw}"
            )
        else:
            escalation_reason = "could not parse model output"
            analysis["reasoning"] = "Model response was not valid JSON; routed to human review."
    else:
        decision = analysis.get("decision", "ESCALATE")
        confidence = float(analysis.get("confidence", 0.0))

    # PRD section 7 — autonomous decision boundary. These overrides always win.
    if escalation_reason is None:
        if adm["amount_claimed"] > ESCALATE_ABOVE_AMOUNT:
            decision = "ESCALATE"
            escalation_reason = f"amount claimed (${adm['amount_claimed']:.2f}) exceeds ${ESCALATE_ABOVE_AMOUNT:.0f} auto-decision limit"
        elif confidence < ESCALATE_BELOW_CONFIDENCE:
            decision = "ESCALATE"
            escalation_reason = f"model confidence ({confidence:.2f}) below {ESCALATE_BELOW_CONFIDENCE:.2f} threshold"
        elif retrieval_score < ESCALATE_BELOW_RETRIEVAL_SCORE:
            decision = "ESCALATE"
            escalation_reason = f"no strong fare rule match (top similarity {retrieval_score:.2f})"

    message = (
        f"Analysis: decision={decision}, confidence={confidence:.2f}. "
        f"{analysis.get('reasoning', '')}"
    )
    if escalation_reason:
        message += f" [Escalation boundary: {escalation_reason}]"

    return {
        "analysis": analysis,
        "decision": decision,
        "confidence": confidence,
        "escalation_reason": escalation_reason,
        "trace": [{"step": "analyze", "message": message, "data": {"decision": decision, "confidence": confidence}}],
    }


def route_decision(state: AgentState) -> Literal["dispute", "pay", "escalate"]:
    return {"DISPUTE": "dispute", "PAY": "pay", "ESCALATE": "escalate"}[state["decision"]]


def _build_evidence(state: AgentState) -> dict:
    return {
        "rule_chunks": [
            {"heading": c["heading"], "source": c["source"], "score": c["score"]}
            for c in state.get("rule_chunks", [])
        ],
        "verification": state.get("verification", {}),
        "citation": state.get("analysis", {}).get("citation", ""),
        "reasoning": state.get("analysis", {}).get("reasoning", ""),
        "retrieval_score": state.get("retrieval_score", 0.0),
        "escalation_reason": state.get("escalation_reason"),
    }


def draft_letter(state: AgentState) -> dict:
    evidence = _build_evidence(state)
    letter = draft_dispute_letter(state["adm"], state.get("pnr"), evidence)
    return {
        "evidence": evidence,
        "output_artifact": letter,
        "trace": [{"step": "draft_letter", "message": "Generated BSPLink-ready dispute letter.", "data": {}}],
    }


def draft_pay_auth_node(state: AgentState) -> dict:
    evidence = _build_evidence(state)
    memo = draft_pay_auth(state["adm"], state.get("pnr"), evidence)
    return {
        "evidence": evidence,
        "output_artifact": memo,
        "trace": [{"step": "draft_pay_auth", "message": "Generated internal pay-authorization memo.", "data": {}}],
    }


def open_case(state: AgentState) -> dict:
    evidence = _build_evidence(state)
    reason = state.get("escalation_reason") or "requires human review"
    ticket = escalate_to_human(state["adm"], state.get("pnr"), evidence, reason)
    return {
        "evidence": evidence,
        "output_artifact": ticket,
        "trace": [{"step": "open_case", "message": f"Opened human review case: {reason}.", "data": {}}],
    }


def submit_decision(state: AgentState) -> dict:
    decision_id = tools.submit_decision(
        adm_id=state["adm_id"],
        decision=state["decision"],
        confidence=state["confidence"],
        evidence=state.get("evidence", {}),
        output_artifact=state.get("output_artifact", ""),
    )
    return {
        "decision_id": decision_id,
        "trace": [{"step": "submit_decision", "message": f"Logged decision {decision_id}.", "data": {"decision_id": decision_id}}],
    }
