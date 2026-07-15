"""LangGraph state machine wiring (PRD section 4 architecture diagram).

    parse_adm -> lookup_booking -> retrieve_rule -> verify_calculation -> analyze
        -> [DISPUTE]  -> draft_letter    -> submit_decision -> END
        -> [PAY]      -> draft_pay_auth  -> submit_decision -> END
        -> [ESCALATE] -> open_case       -> submit_decision -> END
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
    graph.add_edge("submit_decision", END)

    return graph.compile()


_compiled = _build_graph()


def run_agent(adm_id: str) -> AgentState:
    """Synchronous full run — used by POST /agent/run/{adm_id}."""
    initial: AgentState = {"adm_id": adm_id, "trace": []}
    return _compiled.invoke(initial)


def stream_agent(adm_id: str) -> Iterator[dict[str, Any]]:
    """Yields one dict per completed node — used by the WS streaming endpoint."""
    initial: AgentState = {"adm_id": adm_id, "trace": []}
    for update in _compiled.stream(initial, stream_mode="updates"):
        yield update
