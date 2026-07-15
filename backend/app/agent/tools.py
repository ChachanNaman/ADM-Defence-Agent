"""Tools available to the agent (PRD section 4).

Each function here is a plain, independently-testable Python callable — the
LangGraph nodes in app/agent/nodes.py invoke them directly rather than routing
through LLM function-calling, since the graph's control flow is an explicit
state machine, not a tool-calling loop.
"""

import json
import re
import uuid
from datetime import date, datetime, timezone

from app.agent.reference import ROUTE_CORRECT_TAXES
from app.db.database import get_connection, get_cursor

_AP_DIGITS_RE = re.compile(r"(\d+)")


def get_adm(adm_id: str) -> dict | None:
    """Loads the incoming ADM notice (already structured — PRD step 1)."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM adm WHERE adm_id = ?", (adm_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def lookup_booking(ticket_number: str) -> dict | None:
    """lookup_booking(ticket_number) -> PNR record."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM pnr WHERE ticket_number = ?", (ticket_number,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def check_advance_purchase(pnr: dict) -> dict:
    """Category 5 check: does booking-to-departure gap satisfy the fare
    basis's advance-purchase digit? Not every fare basis carries one."""
    match = _AP_DIGITS_RE.search(pnr["fare_basis_code"])
    if not match:
        return {"applicable": False}

    required_days = int(match.group(1))
    booking_date = date.fromisoformat(pnr["booking_date"])
    departure_date = date.fromisoformat(pnr["departure_date"])
    actual_days = (departure_date - booking_date).days

    return {
        "applicable": True,
        "required_days": required_days,
        "actual_days": actual_days,
        "satisfied": actual_days >= required_days,
    }


def check_booking_class_match(pnr: dict) -> dict:
    """Category 4 check: fare basis's leading letter vs. the ticketed class."""
    fare_basis_class = pnr["fare_basis_code"][0].upper()
    ticketed_class = pnr["booking_class"].upper()
    return {
        "fare_basis_class": fare_basis_class,
        "ticketed_class": ticketed_class,
        "match": fare_basis_class == ticketed_class,
    }


def verify_tax_calculation(pnr: dict) -> dict:
    """verify_tax_calculation(pnr) -> recomputed tax breakdown vs. taxes on file."""
    route = (pnr["origin"], pnr["destination"])
    correct_taxes = ROUTE_CORRECT_TAXES.get(route)
    if correct_taxes is None:
        return {"applicable": False}

    taxes_on_file = pnr["taxes"]
    shortfall = round(correct_taxes - taxes_on_file, 2)
    return {
        "applicable": True,
        "taxes_on_file": taxes_on_file,
        "correct_taxes": correct_taxes,
        "shortfall": shortfall,
        "under_collected": shortfall > 0.01,
    }


def submit_decision(
    adm_id: str,
    decision: str,
    confidence: float,
    evidence: dict,
    output_artifact: str,
) -> str:
    """submit_decision(decision, evidence) -> writes to decision_log, returns decision_id."""
    decision_id = f"DEC-{uuid.uuid4().hex[:10]}"
    with get_cursor() as cur:
        cur.execute(
            """INSERT INTO decision_log
               (decision_id, adm_id, decision, confidence, evidence_json, output_artifact, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                decision_id,
                adm_id,
                decision,
                confidence,
                json.dumps(evidence),
                output_artifact,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
    return decision_id
