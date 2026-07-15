export interface PNR {
  pnr_id: string
  ticket_number: string
  passenger_name: string
  origin: string
  destination: string
  fare_basis_code: string
  booking_class: string
  fare_amount: number
  taxes: number
  booking_date: string
  departure_date: string
  agent_id: string
  gds: string
}

export interface ADMListItem {
  adm_id: string
  ticket_number: string
  airline_code: string
  reason_code: string
  amount_claimed: number
  issue_date: string
  dispute_deadline: string
}

export interface ADM extends ADMListItem {
  reason_text: string
  pnr: PNR | null
}

export type Decision = 'DISPUTE' | 'PAY' | 'ESCALATE'

export interface DecisionRecord {
  decision_id: string
  adm_id: string
  decision: Decision
  confidence: number
  evidence_json: string
  output_artifact: string
  timestamp: string
}
