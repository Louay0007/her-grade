# Matching evidence log — T-M1..M7
- Date: 2026-10-23 · `pytest -q` → all pass (see CI).
- T-M1 collective 11+9=20kg rosemary premium, window 15–25 Oct, QR required → total_g 20000, partial=false, mixed_grades=false.
- T-M2 wrong herb (mint) → herb_mismatch. T-M3 standard vs premium → grade_below_required.
- T-M4 harvest 09-01 → harvest_too_old. T-M5 avail 0 → unavailable. T-M6 qr "" → missing_qr.
- T-M7 premium+standard vs standard req → mixed_grades=true, lines keep separate grades (never merged silently).
- API smoke: batch create → 5 portions + idempotent retry + Mode A stop_alert → finish QR → req-20kg matches 20000 → order 11+9 → producer A/B + buyer confirm → confirmed + avail decremented → pricing 10/2.0/40 → /b/ page 200, herb present, no private contacts.
