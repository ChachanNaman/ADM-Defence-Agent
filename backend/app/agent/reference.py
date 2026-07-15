"""Static reference data backing the agent's deterministic verification tools.

Both tables below are "published tariff" facts an agent would normally pull
from a carrier's revenue accounting system — here they're hardcoded because
this is a demo corpus of 10 routes, not a live tax/fare engine.
"""

# (origin, destination) -> correct total government tax + carrier surcharge,
# per the fare basis actually ticketed. Compared against pnr.taxes to catch
# under-collection at the point of sale (PRD tool: verify_tax_calculation).
ROUTE_CORRECT_TAXES: dict[tuple[str, str], float] = {
    ("DFW", "ORD"): 45.30,
    ("LAX", "MIA"): 38.00,
    ("DEL", "KUL"): 74.50,
    ("AUH", "JFK"): 210.00,
    ("NRT", "SIN"): 61.20,
    ("NRT", "LHR"): 480.00,
    ("DEL", "LHR"): 343.40,  # YQ fuel surcharge + gov't tax under-filed at ticketing
    ("BOM", "DXB"): 58.00,
    ("DXB", "JFK"): 245.00,
    ("DXB", "CDG"): 95.00,
}
