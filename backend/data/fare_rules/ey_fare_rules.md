# Etihad Airways — Published Fare Rules Reference
**Airline code:** EY · **Distribution:** GDS filed tariff (ATPCO) · **Document type:** Agency-facing fare rule summary
**Applies to fare bases:** Q7NR, HLXAP7 (international network)

---

## IATA Traffic Conference Area Reference

Fare construction and open-jaw/stopover combinability rules for EY international fares are frequently conditioned on whether all sectors of an itinerary fall within a single IATA Traffic Conference Area.

| Area | Coverage | Relevant airports in this network |
|---|---|---|
| **Area 1 (TC1)** | The Americas | DFW, ORD, LAX, MIA, JFK |
| **Area 2 (TC2)** | Europe, Middle East, Africa | LHR, CDG, AUH, DXB |
| **Area 3 (TC3)** | Asia, South Asia, South-East Asia, South-West Pacific | DEL, BOM, BKK, KUL, NRT, SIN |

## Fare Basis Code Legend

| Segment | Meaning |
|---|---|
| 1st letter | Booking class |
| `LX` | Fare family marker (Leisure Excursion) |
| `AP` + digits | Category 5 advance-purchase requirement, in days |
| Bare digit (no `AP`) | Category 5 advance-purchase requirement, in days |

---

## Q7NR — Economy Discount (International)

- **Category 5 (Advance Res/Ticketing):** Booking and ticketing at least **7 days** before departure.
- **Category 4 (Flight Application / Routing) — Open-Jaw & Stopover Combinability:** Multi-sector open-jaw or single-stop itineraries are permitted **without additional routing surcharge or split-ticket repricing whenever every sector of the itinerary falls within the same single IATA Traffic Conference Area** (see table above). Itineraries that cross Area boundaries (e.g., Area 2 to Area 3) require separate fare construction per Area and may be subject to a routing surcharge.
- **Category 6 (Minimum Stay):** Not filed for this fare basis.
- **Category 16:** Non-refundable.

*Worked example: an itinerary routed Delhi (DEL) – Bangkok (BKK) – Kuala Lumpur (KUL) has both sectors entirely within Area 3. This is a same-Area itinerary and is priced under the single through fare with no routing surcharge — it is compliant with Q7NR Category 4 as filed.*

## HLXAP7 — Premium Economy Excursion

- **Category 5 (Advance Res/Ticketing):** Booking and ticketing at least **7 days** before departure (the `AP7` suffix).
- **Category 6 (Minimum Stay):** Separate and independent from the advance-purchase requirement above. Outbound and return travel must span **at least 6 nights at the destination, or include the first Saturday night following arrival, whichever is less restrictive.** This requirement is enforced against the passenger's actual travel dates, which are recorded in the carrier's own departure-control system (DCS) at the time of the return flight — not in the booking/ticketing PNR record held by the agency. Agencies do not have independent visibility into completed travel dates and cannot self-verify Category 6 compliance from the fare record alone; EY's DCS-sourced minimum-stay audit is the authoritative source for this category. Absent a specific PNR remark documenting an approved waiver, EY's minimum-stay ADMs on HLXAP7 reflect EY's own post-travel audit and should be treated as accurate.
- **Category 4:** Round-trip only, any EY international routing ex-AUH.
- **Category 16:** Non-refundable; minimum-stay non-compliance is recalculated to the next higher non-restricted fare, difference billed via ADM.
