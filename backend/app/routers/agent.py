import asyncio
import queue
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from app.agent.graph import run_agent as run_agent_graph
from app.agent.graph import stream_agent
from app.db.database import get_db
from app.schemas import DecisionOut

router = APIRouter()


@router.post("/agent/run/{adm_id}", response_model=DecisionOut)
def run_agent(adm_id: str, conn: sqlite3.Connection = Depends(get_db)):
    adm_row = conn.execute("SELECT 1 FROM adm WHERE adm_id = ?", (adm_id,)).fetchone()
    if adm_row is None:
        raise HTTPException(status_code=404, detail=f"ADM {adm_id} not found")

    final_state = run_agent_graph(adm_id)

    row = conn.execute(
        "SELECT * FROM decision_log WHERE decision_id = ?", (final_state["decision_id"],)
    ).fetchone()
    return DecisionOut(**dict(row))


@router.websocket("/ws/agent/{adm_id}")
async def ws_run_agent(websocket: WebSocket, adm_id: str):
    """Streams normalized step_start/step/done events straight from
    stream_agent — the demo's live tool-call timeline (PRD v2 change 1).
    Runs the blocking LangGraph stream in a worker thread and bridges each
    chunk back onto the event loop via a queue."""
    await websocket.accept()

    loop = asyncio.get_event_loop()
    events: "queue.Queue" = queue.Queue()
    _SENTINEL = object()

    def drain():
        try:
            for update in stream_agent(adm_id):
                loop.call_soon_threadsafe(events.put_nowait, update)
        except Exception as exc:  # surface node failures to the client instead of hanging it
            loop.call_soon_threadsafe(events.put_nowait, {"__error__": str(exc)})
        finally:
            loop.call_soon_threadsafe(events.put_nowait, _SENTINEL)

    loop.run_in_executor(None, drain)

    try:
        while True:
            update = await loop.run_in_executor(None, events.get)
            if update is _SENTINEL:
                break
            if "__error__" in update:
                await websocket.send_json({"type": "error", "message": update["__error__"]})
                break

            await websocket.send_json(update)
            if update.get("type") == "done":
                break
    except WebSocketDisconnect:
        return
    finally:
        await websocket.close()
