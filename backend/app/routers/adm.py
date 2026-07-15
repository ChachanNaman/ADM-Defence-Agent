import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.db.database import get_db
from app.schemas import ADMListItem, ADMOut, PNROut

router = APIRouter()


@router.get("/adm", response_model=list[ADMListItem])
def list_adms(conn: sqlite3.Connection = Depends(get_db)):
    rows = conn.execute("SELECT * FROM adm ORDER BY issue_date").fetchall()
    return [ADMListItem(**dict(row)) for row in rows]


@router.get("/adm/{adm_id}", response_model=ADMOut)
def get_adm(adm_id: str, conn: sqlite3.Connection = Depends(get_db)):
    adm_row = conn.execute("SELECT * FROM adm WHERE adm_id = ?", (adm_id,)).fetchone()
    if adm_row is None:
        raise HTTPException(status_code=404, detail=f"ADM {adm_id} not found")

    pnr_row = conn.execute(
        "SELECT * FROM pnr WHERE ticket_number = ?", (adm_row["ticket_number"],)
    ).fetchone()

    adm = dict(adm_row)
    adm["pnr"] = PNROut(**dict(pnr_row)) if pnr_row else None
    return ADMOut(**adm)
