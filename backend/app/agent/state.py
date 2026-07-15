import operator
from typing import Annotated, Any, TypedDict


class TraceEvent(TypedDict):
    step: str
    message: str
    data: dict[str, Any]


class AgentState(TypedDict, total=False):
    adm_id: str
    adm: dict[str, Any]
    pnr: dict[str, Any] | None

    rule_chunks: list[dict[str, Any]]
    retrieval_score: float

    verification: dict[str, Any]

    analysis: dict[str, Any]
    decision: str
    confidence: float
    escalation_reason: str | None

    evidence: dict[str, Any]
    output_artifact: str
    decision_id: str

    trace: Annotated[list[TraceEvent], operator.add]
