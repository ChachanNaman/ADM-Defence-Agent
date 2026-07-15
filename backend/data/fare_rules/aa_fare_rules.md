# American Airlines — Published Fare Rules Reference
**Airline code:** AA · **Distribution:** GDS filed tariff (ATPCO) · **Document type:** Agency-facing fare rule summary
**Applies to fare bases:** Q7NR, K7NR, YOW (domestic US network)

---

## Fare Basis Code Legend (AA domestic economy)

AA domestic fare basis codes follow the structure `[Booking Class][Fare Family][Modifiers]`.

| Segment | Meaning |
|---|---|
| 1st letter | Booking class (Q, K, Y, ...) |
| Digit (e.g. `7`) | **Category 5 — Advance Reservation/Ticketing**: minimum number of days before departure that the booking must be made and ticketed. This digit does **not** by itself imply a Category 6 (Minimum Stay) requirement — the two categories are filed independently and only apply where explicitly stated below. |
| `NR` | **Category 16 — Penalties**: fare is non-refundable. |
| `OW` | One-way fare, no advance-purchase requirement, walk-up eligible. |

---

## Q7NR — Economy Value

- **Category 5 (Advance Res/Ticketing):** Reservations must be made and the ticket issued at least **7 days** prior to departure.
- **Category 6 (Minimum Stay):** **Not filed for this fare basis.** Q7NR carries no minimum-stay restriction. (Do not confuse the "7" advance-purchase digit with a minimum-stay night count — this is a common manual ADM-issuance error and is disputable on its face when the sole cited defect is minimum stay.)
- **Category 4 (Flight Application / Routing):** Valid for one-way or round-trip domestic travel, any AA/oneworld domestic routing.
- **Category 16 (Penalties):** Non-refundable; date-change fee applies.

## K7NR — Economy Saver

- **Category 5 (Advance Res/Ticketing):** Reservations must be made and ticketed at least **7 days** prior to departure.
- **Category 4 (Flight Application / Routing):** **Round-trip travel only.** K7NR is not filed for one-way itineraries. A one-way itinerary ticketed under K7NR must be reissued to fare basis **YOW** (Economy One-Way, no advance-purchase requirement, no round-trip discount applied). Agencies that ticket a one-way journey under K7NR in error are liable for the fare difference between K7NR and YOW.
- **Category 16 (Penalties):** Non-refundable.

## YOW — Economy One-Way

- **Category 5:** No advance-purchase requirement.
- **Category 4:** One-way travel only, any domestic routing.
- Filed fare level is higher than the round-trip-only discount fares (Q7NR, K7NR) to compensate for the lack of a round-trip commitment.

---

## Category 16 — Debit Memo Policy Notes

AA issues ADMs under reason code 01 (fare calculation error) when GDS pricing does not match the filed tariff for the booked fare basis and routing. Agencies may dispute an ADM where the cited defect does not correspond to a rule actually filed against the ticketed fare basis, or where the ticketed itinerary does not match the itinerary description in the memo.
