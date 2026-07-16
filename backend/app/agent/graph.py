"""LangGraph state machine wiring (PRD section 4 architecture diagram).

    parse_adm -> lookup_booking -> retrieve_rule -> verify_calculation -> analyze
        -> [DISPUTE]  -> draft_letter    -> submit_decision -> notify_reviewer -> END
        -> [PAY]      -> draft_pay_auth  -> submit_decision -> notify_reviewer -> END
        -> [ESCALATE] -> open_case       -> submit_decision -> notify_reviewer -> END
"""

from typing import Any, Iterator

from langgraph.graph import END, StateGraph

from app.agent import nodes
from app.agent.state import AgentState


def _build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("parse_adm", nodes.parse_adm)
    graph.add_node("lookup_booking", nodes.lookup_booking)
    graph.add_node("retrieve_rule", nodes.retrieve_rule)
    graph.add_node("verify_calculation", nodes.verify_calculation)
    graph.add_node("analyze", nodes.analyze)
    graph.add_node("draft_letter", nodes.draft_letter)
    graph.add_node("draft_pay_auth", nodes.draft_pay_auth_node)
    graph.add_node("open_case", nodes.open_case)
    graph.add_node("submit_decision", nodes.submit_decision)
    graph.add_node("notify_reviewer", nodes.notify_reviewer)

    graph.set_entry_point("parse_adm")
    graph.add_edge("parse_adm", "lookup_booking")
    graph.add_edge("lookup_booking", "retrieve_rule")
    graph.add_edge("retrieve_rule", "verify_calculation")
    graph.add_edge("verify_calculation", "analyze")

    graph.add_conditional_edges(
        "analyze",
        nodes.route_decision,
        {"dispute": "draft_letter", "pay": "draft_pay_auth", "escalate": "open_case"},
    )

    graph.add_edge("draft_letter", "submit_decision")
    graph.add_edge("draft_pay_auth", "submit_decision")
    graph.add_edge("open_case", "submit_decision")
    graph.add_edge("submit_decision", "notify_reviewer")
    graph.add_edge("notify_reviewer", END)

    return graph.compile()


_compiled = _build_graph()


def run_agent(adm_id: str) -> AgentState:
    """Synchronous full run — used by POST /agent/run/{adm_id}."""
    initial: AgentState = {"adm_id": adm_id, "trace": []}
    return _compiled.invoke(initial)


def stream_agent(adm_id: str) -> Iterator[dict[str, Any]]:
    """Yields normalized wire-format events for the WS streaming endpoint:
    {"type": "step_start", "node": ...} when a node begins (emitted by the
    node itself via get_stream_writer — PRD v2 change 1), {"type": "step",
    "node": ..., "events": [...]} when it completes, and finally
    {"type": "done", "decision_id": ...} once notify_reviewer — the actual
    last node — completes."""
    initial: AgentState = {"adm_id": adm_id, "trace": []}
    decision_id = None
    for mode, chunk in _compiled.stream(initial, stream_mode=["updates", "custom"]):
        if mode == "custom":
            yield {"type": "step_start", "node": chunk["node"]}
            continue

        (node_name, delta), = chunk.items()
        trace_events = delta.pop("trace", [])
        yield {"type": "step", "node": node_name, "events": trace_events}

        if node_name == "submit_decision":
            decision_id = delta.get("decision_id")
        if node_name == "notify_reviewer":
            yield {"type": "done", "decision_id": decision_id}
