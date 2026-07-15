# Air India — Published Fare Rules Reference
**Airline code:** AI · **Distribution:** GDS filed tariff (ATPCO) · **Document type:** Agency-facing fare rule summary
**Applies to fare bases:** YEE30, MLXSC (international network)

---

## Fare Basis Code Legend

| Segment | Meaning |
|---|---|
| 1st letter | Booking class |
| `EE` | Fare family marker (Economy Excursion) |
| Trailing digits (e.g. `30`) | Category 5 advance-purchase requirement, in days |
| `LX` | Fare family marker (Leisure Excursion) |
| `SC` | **Schedule Change waiver designation.** This suffix is appended by AI's own reissue system at the time of ticketing when a fare is reissued as a direct consequence of an airline-initiated schedule/equipment change. Its presence on the ticketed fare basis is a system-generated marker, not an agency entry. |

---

## YEE30 — Economy Excursion

- **Category 5 (Advance Res/Ticketing):** Booking and ticketing at least **30 days** before departure.
- **Category 7 (Taxes/Fees/Charges — YQ Fuel Surcharge):** Long-haul India–Europe sectors (e.g., DEL–LHR, BOM–LHR, DEL–CDG) carry a carrier-imposed YQ fuel surcharge in addition to government-imposed taxes (departure tax, passenger service fee, security fee). Combined YQ + government tax/fee total for DEL–LHR under YEE30 is approximately **USD 343** as of the applicable fare filing, subject to periodic revision without notice. Under-collection of YQ and/or government taxes at the point of sale is an agency liability recoverable via ADM per the GDS ticketing agreement (Category 16), irrespective of the base fare calculation being otherwise correct.
- **Category 16:** Non-refundable.

## MLXSC — Economy Classic (Schedule-Change Reissue)

- **Category 5:** No advance-purchase requirement (post-reissue fare).
- **Category 15 (Reissue/Revalidation) — Airline-Initiated Schedule Change:** Where AI initiates an equipment or schedule change of 90 minutes or more affecting a ticketed passenger, any resulting mandatory reissue is fare-protected: the passenger is rebooked on the nearest available service at **no additional fare collection**, and the fare difference (if any) between the original and reissued itinerary is **waived by AI, not payable by the agency.** AI's reissue system appends the `SC` suffix to the reissued fare basis code specifically to flag this waiver on the ticket record. **A ticketed fare basis ending in `SC` is AI's own confirmation that the reissue was carrier-initiated and fare-protected.** ADMs seeking to collect a fare difference against a fare basis already carrying the `SC` waiver designation are contradicted by the ticket's own fare basis code and should not be paid without a documented exception from AI Revenue Accounts.
- **Category 16:** Non-refundable (base fare rules of the original ticket carry over under the waiver).
