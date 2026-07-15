"""Runs the agent against all 10 seed ADMs and diffs decisions against the
expected labels recorded at seed time (PRD Day 2: "verify decision
distribution matches expected labels"). Run: `python -m app.eval_seed`
"""

import json

from app.agent.graph import run_agent
from app.config import BACKEND_DIR
from app.db.database import get_cursor


def main() -> None:
    expected = json.loads((BACKEND_DIR / "data" / "seed" / "expected_labels.json").read_text())

    with get_cursor() as cur:
        cur.execute("DELETE FROM decision_log")

    correct = 0
    for adm_id, expected_decision in expected.items():
        state = run_agent(adm_id)
        actual = state["decision"]
        ok = actual == expected_decision
        correct += ok
        marker = "OK  " if ok else "MISS"
        reason = state.get("escalation_reason") or ""
        print(
            f"{marker} {adm_id}: expected={expected_decision:<9} actual={actual:<9} "
            f"confidence={state['confidence']:.2f} {('(' + reason + ')') if reason else ''}"
        )

    print(f"\n{correct}/{len(expected)} match expected labels.")


if __name__ == "__main__":
    main()
