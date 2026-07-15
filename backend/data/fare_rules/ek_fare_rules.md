# Emirates — Published Fare Rules Reference
**Airline code:** EK · **Distribution:** GDS filed tariff (ATPCO) · **Document type:** Agency-facing fare rule summary
**Applies to fare bases:** TLXAP21, BLXMC (international network)

---

## Fare Basis Code Legend

| Segment | Meaning |
|---|---|
| 1st letter | Booking class — this letter is the definitive statement of the booking class the fare basis requires. It must match the `booking_class` recorded on the ticket. |
| `LX` | Fare family marker (Leisure Excursion) |
| `AP` + digits | Category 5 advance-purchase requirement, in days |
| `MC` | Mixed-cabin / tour-code fare marker (see note below) |

---

## TLXAP21 — Economy Saver

- **Category 5 (Advance Res/Ticketing):** Booking and ticketing at least **21 days** before departure.
- **Category 4 (Flight Application):** Booking class **T** required — this is fixed by the first letter of the fare basis code itself (`T`LXAP21). The ticketed `booking_class` field on the PNR is the authoritative record of which class was actually sold; compare it directly against the fare basis code's leading letter to confirm or refute a booking-class-mismatch claim.
- **Category 16:** Non-refundable.

## BLXMC — Economy Classic (Tour Code / Mixed Cabin)

- **Category 5:** No advance-purchase requirement.
- **Category 4:** Booking class **B**.
- **Note on `MC` (mixed-cabin) fares:** BLXMC is used when an itinerary combines segments across more than one cabin under a single ticket, frequently in connection with a wholesale tour-code contract negotiated directly between the consolidator and EK Cargo & Commercial outside the standard published tariff. **Tour-code-contracted fares are not filed in the standard ATPCO tariff and are not fully represented in this rule manual** — their terms live in the bilateral tour-code agreement, not in GDS-visible fare rules. Disputes turning on tour-code applicability to an exchanged/mixed-cabin segment cannot be fully adjudicated from the published fare rules alone and are referred to EK account management / the tour-code contract holder for a case-by-case determination.
