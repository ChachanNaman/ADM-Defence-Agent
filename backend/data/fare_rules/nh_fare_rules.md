# ANA (All Nippon Airways) — Published Fare Rules Reference
**Airline code:** NH · **Distribution:** GDS filed tariff (ATPCO) · **Document type:** Agency-facing fare rule summary
**Applies to fare bases:** VLXAP14, CFLEX (international network)

---

## Fare Basis Code Legend

| Segment | Meaning |
|---|---|
| 1st letter | Booking class |
| `LX` | Fare family marker (Leisure Excursion) |
| `AP` + digits | Category 5 advance-purchase requirement, in days |
| `FLEX` | Fully flexible fare family — no advance purchase, no minimum stay, free date/route changes |

---

## Category 10 — Combinations / Married Segment Logic (network-wide)

Married segment logic governs how a single fare component that contains **two or more directly connecting flight coupons** must be priced as one combined unit rather than as separately-priced origin-and-destination (O&D) pairs. This category applies **only** to itineraries with two or more connecting flight coupons under one fare component.

**A single nonstop flight coupon between one origin and one destination is, by definition, not a married-segment combination — Category 10 does not apply to single-segment O&Ds.** Married-segment ADMs raised against a ticketed itinerary that consists of one direct flight coupon are raised against an itinerary structure that does not exist on the ticket and should be verified against the actual ticketed coupons before being upheld.

## VLXAP14 — Economy Special

- **Category 5 (Advance Res/Ticketing):** Booking and ticketing at least **14 days** before departure.
- **Category 4 (Flight Application / Routing):** Valid for direct/nonstop and single-connection international itineraries. Where the ticketed itinerary is a single nonstop O&D, Category 10 (married segment) is not applicable — see above.
- **Category 6 (Minimum Stay):** Not filed for this fare basis.
- **Category 16:** Non-refundable.

## CFLEX — Business Flexible

- **Category 5:** No advance-purchase requirement.
- **Category 6:** No minimum stay.
- **Category 15 (Reissue/Revalidation):** Fully flexible; reissues are permitted without fare recalculation subject to fare-family rules in effect at the time of reissue. Reissue fare recalculation discrepancies on flexible business fares typically involve multiple co-terminal fare filings that were in effect on different dates and require the carrier's Fares Audit desk to confirm the exact filing that applied at reissue — the agency-visible GDS record alone is not always sufficient to confirm which of several concurrently filed CFLEX fare levels governs a given reissue. High-value CFLEX reissue disputes should be routed through Fares Audit rather than resolved solely from the PNR fare record.
