"""Seeds 10 PNRs and 10 ADMs: 5 disputable / 3 legit / 2 ambiguous.

Expected agent decisions are not part of the schema (the agent must derive
them independently) but are recorded in data/seed/expected_labels.json for
verifying the agent's judgment once it's built (PRD Day 2).
"""

import json
from pathlib import Path

from app.db.database import get_cursor, init_db, BACKEND_DIR

PNR_SEED = [
    ("PNR001", "0012345678901", "Sarah Chen", "DFW", "ORD", "Q7NR", "Q", 210.00, 45.30, "2026-05-10", "2026-06-15", "AGT-102", "Sabre"),
    ("PNR002", "0016789012345", "Marcus Webb", "LAX", "MIA", "K7NR", "K", 189.00, 38.00, "2026-05-02", "2026-06-01", "AGT-118", "Sabre"),
    ("PNR003", "6073456789012", "Priya Raman", "DEL", "KUL", "Q7NR", "Q", 265.00, 74.50, "2026-04-20", "2026-07-05", "AGT-045", "Amadeus"),
    ("PNR004", "6079012345678", "James O'Connor", "AUH", "JFK", "HLXAP7", "H", 720.00, 210.00, "2026-03-15", "2026-04-10", "AGT-045", "Amadeus"),
    ("PNR005", "2053456789012", "Yuki Tanaka", "NRT", "SIN", "VLXAP14", "V", 340.00, 61.20, "2026-05-18", "2026-06-20", "AGT-077", "Sabre"),
    ("PNR006", "2059876543210", "Emma Whitfield", "NRT", "LHR", "CFLEX", "C", 2100.00, 480.00, "2026-06-01", "2026-06-25", "AGT-077", "Sabre"),
    ("PNR007", "0983456789012", "Rahul Mehta", "DEL", "LHR", "YEE30", "Y", 610.00, 175.40, "2026-04-25", "2026-05-30", "AGT-063", "Galileo"),
    ("PNR008", "0987654321098", "Anjali Kapoor", "BOM", "DXB", "MLXSC", "M", 245.00, 58.00, "2026-02-10", "2026-06-05", "AGT-063", "Galileo"),
    ("PNR009", "1765432109876", "David Osei", "DXB", "JFK", "TLXAP21", "T", 890.00, 245.00, "2026-05-05", "2026-06-10", "AGT-091", "Amadeus"),
    ("PNR010", "1769012345678", "Fatima Al-Sayed", "DXB", "CDG", "BLXMC", "B", 410.00, 95.00, "2026-04-01", "2026-05-15", "AGT-091", "Amadeus"),
]

ADM_SEED = [
    ("ADM001", "0012345678901", "AA", "01", "Fare calculation error - minimum stay requirement not satisfied for fare basis Q7NR round-trip booking.", 245.00, "2026-07-02", "2026-07-16", "DISPUTE"),
    ("ADM002", "0016789012345", "AA", "01", "Fare calculation error - incorrect fare basis applied; correct fare basis for one-way LAX-MIA is YOW, not K7NR.", 178.00, "2026-07-04", "2026-07-18", "PAY"),
    ("ADM003", "6073456789012", "EY", "01", "Fare calculation error - open-jaw routing via Bangkok not permitted under fare basis Q7NR.", 340.00, "2026-07-03", "2026-07-17", "DISPUTE"),
    ("ADM004", "6079012345678", "EY", "01", "Minimum stay requirement not met - passenger returned before the required minimum stay under fare basis HLXAP7.", 295.00, "2026-07-05", "2026-07-19", "PAY"),
    ("ADM005", "2053456789012", "NH", "02", "Married segment logic violation - connecting segments priced incorrectly as separate O&Ds.", 220.00, "2026-07-06", "2026-07-20", "DISPUTE"),
    ("ADM006", "2059876543210", "NH", "01", "Fare calculation error on business class fare CFLEX - reissue fare recalculation discrepancy.", 612.00, "2026-07-07", "2026-07-21", "ESCALATE"),
    ("ADM007", "0983456789012", "AI", "04", "Under-collected YQ fuel surcharge and taxes on fare basis YEE30.", 168.00, "2026-07-08", "2026-07-22", "PAY"),
    ("ADM008", "0987654321098", "AI", "10", "Improper ticketing/reissue - schedule change not processed correctly, fare difference owed.", 205.00, "2026-07-09", "2026-07-23", "DISPUTE"),
    ("ADM009", "1765432109876", "EK", "01", "Booking class mismatch - fare basis TLXAP21 requires class T but ticket shows class Q.", 275.00, "2026-07-10", "2026-07-24", "DISPUTE"),
    ("ADM010", "1769012345678", "EK", "09", "Tour code discrepancy on mixed-cabin exchange - applicability of original fare rules to exchanged segment unclear.", 330.00, "2026-07-11", "2026-07-25", "ESCALATE"),
]


def seed() -> None:
    init_db()
    with get_cursor() as cur:
        cur.execute("DELETE FROM decision_log")
        cur.execute("DELETE FROM adm")
        cur.execute("DELETE FROM pnr")
        cur.executemany(
            """INSERT INTO pnr (pnr_id, ticket_number, passenger_name, origin, destination,
                                fare_basis_code, booking_class, fare_amount, taxes,
                                booking_date, departure_date, agent_id, gds)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            PNR_SEED,
        )
        cur.executemany(
            """INSERT INTO adm (adm_id, ticket_number, airline_code, reason_code, reason_text,
                                amount_claimed, issue_date, dispute_deadline)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [row[:8] for row in ADM_SEED],
        )

    expected_labels = {row[0]: row[8] for row in ADM_SEED}
    labels_path = BACKEND_DIR / "data" / "seed" / "expected_labels.json"
    labels_path.write_text(json.dumps(expected_labels, indent=2) + "\n")

    print(f"Seeded {len(PNR_SEED)} PNRs and {len(ADM_SEED)} ADMs.")
    print(f"Expected labels written to {labels_path}")


if __name__ == "__main__":
    seed()
