"""Output-artifact generators: dispute letter, pay authorization, escalation ticket.

PRD tools: draft_dispute_letter(adm, pnr, evidence), escalate_to_human(reason, case).
The pay-authorization artifact is the equivalent generator for the PAY branch
(the PRD's graph diagram names its node draft_pay_auth).
"""

import json

from app.agent.llm import complete_text

_LETTER_SYSTEM = """You draft short, factual, unemotional agency debit memo (ADM) \
dispute letters for a travel consolidator's back office. Output ONLY the letter \
body — no preamble, no markdown, no explanation before or after. The letter must:
- be addressed to the airline's Revenue Accounts / ADM department
- reference the ADM number, ticket number, and amount claimed
- state the specific fare rule citation and the specific reason the ADM is incorrect
- request cancellation/reversal of the ADM
- close with a formal sign-off placeholder for the agency
- be ready to paste into BSPLink, under 250 words"""

_PAY_AUTH_SYSTEM = """You draft short internal pay-authorization memos for a travel \
consolidator's back office, authorizing payment of a legitimate agency debit memo (ADM). \
Output ONLY the memo body — no preamble, no markdown. The memo must:
- reference the ADM number, ticket number, and amount claimed
- state the specific, factual justification for why the claim is valid
- authorize payment and note the BSP payment deadline
- close with an approver sign-off placeholder
- be under 150 words"""

_ESCALATION_SYSTEM = """You draft short internal case-escalation tickets for a travel \
consolidator's back office, routing an ambiguous agency debit memo (ADM) to a human \
fares analyst. Output ONLY the ticket body — no preamble, no markdown. The ticket must:
- reference the ADM number, ticket number, and amount claimed
- state exactly why the case cannot be auto-resolved (what's missing, conflicting, or uncertain)
- list the specific facts/evidence gathered so far so the analyst doesn't have to re-pull them
- recommend a concrete next step for the analyst
- be under 150 words"""


def _case_facts(adm: dict, pnr: dict | None, evidence: dict) -> str:
    return json.dumps({"adm": adm, "pnr": pnr, "evidence": evidence}, indent=2, default=str)


def _fallback_artifact(kind: str, adm: dict, evidence: dict, reason: str | None = None) -> str:
    """Deterministic, no-LLM artifact used when the model provider is down.

    A drafting failure must never surface as a 500 — the case still has to
    produce *something* a human can act on, even with the LLM unavailable.
    """
    lines = [
        f"[AUTO-GENERATED FALLBACK — LLM unavailable, drafted without narrative text]",
        f"Type: {kind}",
        f"ADM: {adm['adm_id']}  Ticket: {adm['ticket_number']}  Amount claimed: ${adm['amount_claimed']:.2f}",
        f"Airline: {adm['airline_code']}  Reason code: {adm['reason_code']}",
        f"Airline's stated reason: {adm['reason_text']}",
    ]
    if reason:
        lines.append(f"Escalation reason: {reason}")
    citation = evidence.get("citation")
    if citation:
        lines.append(f"Rule citation found: {citation}")
    if evidence.get("reasoning"):
        lines.append(f"Automated reasoning: {evidence['reasoning']}")
    verification = evidence.get("verification", {})
    if verification:
        lines.append(f"Verification results: {json.dumps(verification, default=str)}")
    lines.append("A human analyst should review the above and complete this case manually.")
    return "\n".join(lines)


def draft_dispute_letter(adm: dict, pnr: dict | None, evidence: dict) -> str:
    try:
        return complete_text(_LETTER_SYSTEM, _case_facts(adm, pnr, evidence))
    except RuntimeError:
        return _fallback_artifact("DISPUTE letter", adm, evidence)


def draft_pay_auth(adm: dict, pnr: dict | None, evidence: dict) -> str:
    try:
        return complete_text(_PAY_AUTH_SYSTEM, _case_facts(adm, pnr, evidence))
    except RuntimeError:
        return _fallback_artifact("PAY authorization", adm, evidence)


def escalate_to_human(adm: dict, pnr: dict | None, evidence: dict, reason: str) -> str:
    facts = _case_facts(adm, pnr, evidence)
    try:
        return complete_text(_ESCALATION_SYSTEM, f"Escalation reason: {reason}\n\n{facts}")
    except RuntimeError:
        return _fallback_artifact("ESCALATE case ticket", adm, evidence, reason=reason)
