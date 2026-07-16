import sqlite3
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from app.db.database import get_db
from app.schemas import DecisionOut

router = APIRouter()

_ACTION_LABELS = {
    "approved": "Approved",
    "rejected": "Rejected",
    "request_info": "More information requested",
}


@router.get("/decision/{decision_id}", response_model=DecisionOut)
def get_decision(decision_id: str, conn: sqlite3.Connection = Depends(get_db)):
    row = conn.execute(
        "SELECT * FROM decision_log WHERE decision_id = ?", (decision_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")
    return DecisionOut(**dict(row))


def _set_reviewer_action(
    decision_id: str, action: str, conn: sqlite3.Connection
) -> HTMLResponse:
    row = conn.execute(
        "SELECT 1 FROM decision_log WHERE decision_id = ?", (decision_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")

    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE decision_log SET reviewer_action = ?, reviewer_action_at = ? WHERE decision_id = ?",
        (action, now, decision_id),
    )
    conn.commit()

    label = _ACTION_LABELS[action]
    return HTMLResponse(
        f"<!doctype html><html><body style='font-family: sans-serif; padding: 2rem;'>"
        f"<h2>{label}</h2>"
        f"<p>Decision {decision_id} marked <strong>{action}</strong> at {now}.</p>"
        f"<p>You can close this tab — the reviewer status will update in the app.</p>"
        f"</body></html>"
    )


@router.get("/decision/{decision_id}/approve", response_class=HTMLResponse)
def approve_decision(decision_id: str, conn: sqlite3.Connection = Depends(get_db)):
    return _set_reviewer_action(decision_id, "approved", conn)


@router.get("/decision/{decision_id}/reject", response_class=HTMLResponse)
def reject_decision(decision_id: str, conn: sqlite3.Connection = Depends(get_db)):
    return _set_reviewer_action(decision_id, "rejected", conn)


@router.get("/decision/{decision_id}/request_info", response_class=HTMLResponse)
def request_info_decision(decision_id: str, conn: sqlite3.Connection = Depends(get_db)):
    return _set_reviewer_action(decision_id, "request_info", conn)
