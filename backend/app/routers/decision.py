import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.db.database import get_db
from app.schemas import DecisionOut

router = APIRouter()


@router.get("/decision/{decision_id}", response_model=DecisionOut)
def get_decision(decision_id: str, conn: sqlite3.Connection = Depends(get_db)):
    row = conn.execute(
        "SELECT * FROM decision_log WHERE decision_id = ?", (decision_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")
    return DecisionOut(**dict(row))
