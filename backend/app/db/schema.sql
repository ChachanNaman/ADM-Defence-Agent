CREATE TABLE IF NOT EXISTS pnr (
    pnr_id TEXT PRIMARY KEY,
    ticket_number TEXT UNIQUE NOT NULL,
    passenger_name TEXT NOT NULL,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    fare_basis_code TEXT NOT NULL,
    booking_class TEXT NOT NULL,
    fare_amount REAL NOT NULL,
    taxes REAL NOT NULL,
    booking_date TEXT NOT NULL,
    departure_date TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    gds TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS adm (
    adm_id TEXT PRIMARY KEY,
    ticket_number TEXT NOT NULL REFERENCES pnr (ticket_number),
    airline_code TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    reason_text TEXT NOT NULL,
    amount_claimed REAL NOT NULL,
    issue_date TEXT NOT NULL,
    dispute_deadline TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decision_log (
    decision_id TEXT PRIMARY KEY,
    adm_id TEXT NOT NULL REFERENCES adm (adm_id),
    decision TEXT NOT NULL CHECK (decision IN ('DISPUTE', 'PAY', 'ESCALATE')),
    confidence REAL NOT NULL,
    evidence_json TEXT NOT NULL,
    output_artifact TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    reviewer_action TEXT DEFAULT NULL,
    reviewer_action_at TEXT DEFAULT NULL
);
