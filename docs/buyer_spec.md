# Buyer spec — LOCKED P1 (rosemary)
**Status:** LOCKED 23-Oct-2026 · **Herb:** rosemary ONLY (no mint/thyme piles in Phase 1) · **Track:** Track 2 primary (support Track 1+3)

## Buyer (TEST)
- Buyer: demo buyer, Tunis — 20,000g rosemary, grade **premium** (accepted-looking).
- Harvest window: 2026-10-15 → 2026-10-25 (as-entered dates; platform does not verify lab claims).
- Delivery: Tunis · deadline 2026-11-05 · max ask 14.0 DT/kg · needs QR traceability page.

## Grade rule — accepted-looking vs needs-verification (visual screening ONLY)
Camera + laptop CV = visual screening. **Cannot** detect moisture, chemicals, microbes, aroma, food safety. Low-confidence → human review. Accepted still may need moisture/hygiene/lab checks off-platform.
- **Accepted-looking (premium):** green intact needles, uniform green, no yellowing, no woody stems, no dust clumps, no foreign matter, single separated portion, sharp focus.
- **Needs-verification:** ANY of: yellowing/browning, stemmy/woody, dust clumps, foreign leaf/matter, overlap of 2+ portions, blur/occlusion, area too small/large, confidence < 0.75 (v0.1-0.75 initial, calibrate on val).
- Photo refs: `data/raw/rosemary/accepted/` vs `data/raw/rosemary/verify/` (collect 26–30 Oct, ≥300, split by batch 70/15/15, test unseen).

## Demo fulfilment (TEST data)
- Producer A (TEST): batch-A11 — 11,000g premium, harvest 2026-10-20, 12.0 DT/kg.
- Producer B (TEST): batch-B09 — 9,000g premium, harvest 2026-10-21, 12.0 DT/kg.
- Proposal: 11kg + 9kg = 20kg collective. Separate batch IDs + per-producer qty/price preserved. All confirm required (each producer + buyer). Different grades NEVER shown as one uniform grade — offered separately or only with explicit buyer acceptance + separate lines.

## Rejection reasons (hard filters)
herb_mismatch · unavailable · grade_below_required · harvest_too_old/too_new · missing_qr. Rank survivors by visual_sim (experimental) + date + delivery + price/qty fit.

## Price (illustrative ONLY until field validation)
Example: Cprod 8.00 + Cpack 1.00 + Ctrans 0.50 + Cfees 0.50 = 10.00 DT/kg; Psale 12.00 → margin 2.00/kg; 20kg → 40 DT. `POST /api/pricing/calc` warns if Psale < Ctotal. State as entered-cost estimate, never market truth.
