"""Human-in-the-loop reviewer email (PRD v2 change 2).

send_reviewer_email() renders one of three Jinja2 templates depending on
decision type and sends it via SMTP. A failure here must never crash the
agent run — the decision is already committed to decision_log by
submit_decision before this runs, so the caller (nodes.notify_reviewer)
catches EmailSendError and logs it as a non-fatal trace event.
"""

import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid

from jinja2 import Environment, FileSystemLoader

from app.config import (
    BACKEND_DIR,
    BACKEND_PUBLIC_URL,
    FINANCE_REVIEWER_EMAIL,
    FROM_EMAIL,
    OPS_REVIEWER_EMAIL,
    SENIOR_ANALYST_EMAIL,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USER,
)

_TEMPLATES_DIR = BACKEND_DIR / "app" / "agent" / "templates"
_env = Environment(loader=FileSystemLoader(_TEMPLATES_DIR), autoescape=True)

_REVIEWER_CONFIG = {
    "DISPUTE": {"email": OPS_REVIEWER_EMAIL, "template": "email_dispute.html.j2", "role": "Ops team lead"},
    "PAY": {"email": FINANCE_REVIEWER_EMAIL, "template": "email_pay.html.j2", "role": "Finance manager"},
    "ESCALATE": {"email": SENIOR_ANALYST_EMAIL, "template": "email_escalate.html.j2", "role": "Senior analyst"},
}


class EmailSendError(Exception):
    pass


def _verification_strings(evidence: dict) -> dict:
    verification = evidence.get("verification", {})
    ap = verification.get("advance_purchase", {})
    bc = verification.get("booking_class", {})
    tax = verification.get("tax_calculation", {})

    if not ap.get("applicable"):
        advance_purchase_result = "not applicable"
    else:
        advance_purchase_result = (
            f"{'satisfied' if ap['satisfied'] else 'VIOLATED'} "
            f"({ap['actual_days']}d actual vs {ap['required_days']}d required)"
        )

    if bc.get("match") is None:
        class_match_result = "not applicable"
    else:
        class_match_result = (
            f"{'match' if bc['match'] else 'MISMATCH'} "
            f"({bc['ticketed_class']} vs {bc['fare_basis_class']})"
        )

    if not tax.get("applicable"):
        tax_check_result = "not applicable"
    elif tax.get("under_collected"):
        tax_check_result = f"shortfall of ${tax['shortfall']:.2f} found"
    else:
        tax_check_result = "taxes on file match recomputed amount"

    rule_chunks = evidence.get("rule_chunks", [])
    top_rule_chunk_id = rule_chunks[0]["heading"] if rule_chunks else "none retrieved"

    return {
        "advance_purchase_result": advance_purchase_result,
        "class_match_result": class_match_result,
        "tax_check_result": tax_check_result,
        "top_rule_chunk_id": top_rule_chunk_id,
        "top_similarity": f"{evidence.get('retrieval_score', 0.0):.2f}",
        "model_reasoning": evidence.get("reasoning", "") or "(none)",
    }


def send_reviewer_email(
    decision: str,
    adm: dict,
    pnr: dict | None,
    evidence: dict,
    output_artifact: str,
    confidence: float,
    decision_id: str,
) -> dict:
    """Sends the formatted review email to the correct reviewer based on decision type.

    Returns {"sent_to": str, "message_id": str, "timestamp": datetime}.
    Raises EmailSendError on missing config or SMTP failure.
    """
    config = _REVIEWER_CONFIG.get(decision)
    if config is None:
        raise EmailSendError(f"no reviewer routing configured for decision {decision!r}")

    reviewer_email = config["email"]
    if not reviewer_email:
        raise EmailSendError(f"no reviewer email configured for {decision} decisions")
    if not SMTP_USER or not SMTP_PASSWORD:
        raise EmailSendError("SMTP_USER / SMTP_PASSWORD not configured")

    template = _env.get_template(config["template"])
    context = {
        "decision": decision,
        "confidence_pct": round(confidence * 100),
        "adm_id": adm["adm_id"],
        "deadline": adm["dispute_deadline"],
        "reason_text": adm["reason_text"],
        "ticket_number": adm["ticket_number"],
        "amount": adm["amount_claimed"],
        "airline_code": adm["airline_code"],
        "pnr": pnr,
        "output_artifact": output_artifact,
        "escalation_reason": evidence.get("escalation_reason") or "not confident enough to auto-decide",
        "approve_url": f"{BACKEND_PUBLIC_URL}/decision/{decision_id}/approve",
        "reject_url": f"{BACKEND_PUBLIC_URL}/decision/{decision_id}/reject",
        "request_info_url": f"{BACKEND_PUBLIC_URL}/decision/{decision_id}/request_info",
        **_verification_strings(evidence),
    }
    html_body = template.render(**context)

    subject = (
        f"[ADM Defense Agent] {decision} recommended — "
        f"Ticket {adm['ticket_number']} — ${adm['amount_claimed']:.2f}"
    )

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = FROM_EMAIL
    message["To"] = reviewer_email
    message_id = make_msgid()
    message["Message-ID"] = message_id
    message.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(message)
    except (smtplib.SMTPException, OSError) as exc:
        raise EmailSendError(str(exc)) from exc

    return {
        "sent_to": reviewer_email,
        "message_id": message_id,
        "timestamp": datetime.now(timezone.utc),
    }
