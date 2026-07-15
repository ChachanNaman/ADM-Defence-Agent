from pydantic import BaseModel


class PNROut(BaseModel):
    pnr_id: str
    ticket_number: str
    passenger_name: str
    origin: str
    destination: str
    fare_basis_code: str
    booking_class: str
    fare_amount: float
    taxes: float
    booking_date: str
    departure_date: str
    agent_id: str
    gds: str


class ADMListItem(BaseModel):
    adm_id: str
    ticket_number: str
    airline_code: str
    reason_code: str
    amount_claimed: float
    issue_date: str
    dispute_deadline: str


class ADMOut(BaseModel):
    adm_id: str
    ticket_number: str
    airline_code: str
    reason_code: str
    reason_text: str
    amount_claimed: float
    issue_date: str
    dispute_deadline: str
    pnr: PNROut | None = None


class DecisionOut(BaseModel):
    decision_id: str
    adm_id: str
    decision: str
    confidence: float
    evidence_json: str
    output_artifact: str
    timestamp: str
