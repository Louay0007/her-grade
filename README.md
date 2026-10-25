# HER-GRADE — Smart Herb Sorting, Traceability & Collective Marketing

**Track 2** — Supply Chain Fragmentation & Limited Direct Market Access (support: Track 1 repetitive sorting, Track 3 dust/safety).
**Phase 1 deadline: 05 Nov 2026 · Herb LOCKED: rosemary only · Status: runnable slice, tests green.**

Low-cost conveyor visual-inspection station + dust extraction hood + batch QR + collective marketplace for women herb producers. Fully self-hosted, works offline on one laptop. No cloud on the critical path.

> Honesty box: the camera + laptop CV is **visual screening only** — it cannot detect moisture, chemicals, microbes, aroma, or certify food safety. Low-confidence / unusual portions go to human verification. Prices and BOM are planning estimates until field quotes. Surrogate image metrics are pipeline smoke only, never claim-grade.

[![phase1-ci](https://github.com/Louay0007/her-grade/actions/workflows/phase1-ci/badge.svg)](https://github.com/Louay0007/her-grade/actions)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue) ![Tests 16 passing](https://img.shields.io/badge/tests-16_passing-green) ![License MIT (+CC images)](https://img.shields.io/badge/license-MIT-green)

---

## 1. What it does (10-step pipeline)

1. Producer creates a batch (rosemary, harvest date as-entered, locality level).
2. Hopper/gate releases small separated portions onto a slow conveyor (gap ≥ 8 cm, no overlap).
3. Fixed camera captures each portion under fixed LED + enclosed inspection zone.
4. Laptop CV returns **accepted-looking** | **needs-verification** + confidence (threshold `v0.1-0.75` initial, calibrate on val).
5. ESP32/Arduino syncs conveyor + servo flap diverter over USB serial (JSONL 115200).
6. Portion → accepted box OR verification box. Counts logged per portion.
7. Finish batch → totals + batch ID + QR (PNG + public URL).
8. Batch published to the local platform.
9. Buyer requests e.g. 20 kg; matching proposes compatible lots (e.g. 11 kg + 9 kg), scores explained.
10. Each producer confirms, buyer confirms → collective order with separate batch IDs preserved.

Two station modes: **A Supervised** (uncertain → red alert + stop, operator resumes) / **B Unattended** (uncertain → verify box + log, still stops on jam/fault/cover/estop). The e-stop cuts motor power in hardware via relay — software stop is NOT safety.

## 2. Quickstart

```bash
cp .env.example .env
docker compose up --build -d
# app:   http://localhost:8000
# phone (same LAN): http://<laptop-lan-ip>:8080  → scan batch QR
```

Dev without docker (Python 3.12):

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed_demo.py        # TEST data: prod-A 11kg + prod-B 9kg → req-20kg
uvicorn app.main:app --reload --port 8000
```

Verify:

```bash
pytest -q                            # 16 tests: matching T-M1..M7, pricing, vision logic, API smoke, idempotency
ruff check app vision tests scripts && black --check app vision tests scripts
curl localhost:8000/health          # {"ok": true, "herb_locked": "rosemary", ...}
```

## 3. The 8-step jury demo

| # | Step | Where | Expect |
|---|---|---|---|
| 1 | Producer creates rosemary batch | `/producer` → `POST /api/batches` | batch id, grade premium, status open |
| 2 | Feed portions (Mode B) | `POST /api/batches/{id}/portions?mode=B` | `accepted` / `verify` divert, counts grow |
| 3 | Mode A uncertain | same with `?mode=A`, conf 0.4 | `stop_alert`, red alert + stop, operator resumes |
| 4 | Finish → QR | `POST /api/batches/{id}/finish` → `/b/{id}` | QR png + phone-scannable traceability page |
| 5 | Buyer requests 20 kg | `/buyer` → `POST /api/requests` | request id, grade premium, window, max price |
| 6 | Collective proposal | `GET /api/requests/{id}/matches` | 11 kg + 9 kg = 20 kg, scores + reasons |
| 7 | Confirm all | `POST /api/orders` → `/confirm` producer A/B + buyer | `confirmed`, availability decremented, IDs preserved |
| 8 | Price check | `POST /api/pricing/calc` | Ctotal/Mkg/Mtotal + below-cost warning (illustrative) |

Pages: `/` dashboard · `/producer` · `/batch/{id}` detail · `/station` (Mode A/B, stop/resume, e-stop mirror) · `/buyer` (requests, matches, calculator, orders) · `/b/{batch_id}` public QR page (no contacts, no price).

## 4. API reference (minimal, stable for Phase 1)

| Method | Endpoint | Body / Query | Returns |
|---|---|---|---|
| POST | `/api/batches` | `{producer_id, herb_type:"rosemary", harvest_date, locality, grade, unit_ask}` | `{id, herb_type, grade, status}` |
| GET | `/api/batches` | — | list with totals/avail/status/qr |
| GET | `/api/batches/{id}` | — | batch + portion count |
| POST | `/api/batches/{id}/portions?mode=A\|B` | `{id?, image_ref, pred, conf, area_ok, overlap}` (id = idempotency key) | `{target, action, reason, totals}` |
| POST | `/api/batches/{id}/finish` | — | `{qr_url, qr_png, totals, avail_g, status:published}` |
| GET | `/api/batches/{id}/events` | — | portion log |
| GET | `/b/{batch_id}` | — | public traceability HTML (herb, batch, harvest as-entered, locality, qty, timeline; NO contacts/price) |
| POST | `/api/requests` | `{herb_type, qty_need_g, grade_required, harvest_from/to, max_price, delivery_place, deadline, needs_qr}` | `{id, qty_need_g, status}` |
| GET | `/api/requests/{id}/matches` | — | `{lines[{lot_id,batch_id,producer_id,qty_g,unit_price,score,grade}], total_g, partial, mixed_grades, excluded[{lot_id,reason}]}` |
| POST | `/api/orders` | `{request_id, contributions:[{batch_id, qty_g}]}` | `{id, total_g, lines}` |
| POST | `/api/orders/{id}/confirm` | `{role:"producer:x"\|"buyer", producer_id?}` | `{status, all_producers_confirmed, buyer_confirmed}` (confirmed only when ALL confirm) |
| POST | `/api/pricing/calc` | `{cprod,cproc,cpack,ctrans,cfees,psale,qty_kg}` | `{ctotal,mkg,mtotal,below_cost,disclaimer}` |
| GET/POST | `/api/station/status\|mode\|stop\|resume\|estop` | `{mode}` | mode + serial state (software mirror; HW relay is the real e-stop) |
| GET | `/health` | — | `{ok, track, mode, herb_locked}` |

Serial (USB 115200 JSONL): laptop→MCU `divert/mode/stop/resume`; MCU→laptop `sensed/diverted/fault`; heartbeat 1 Hz. Idempotency: resend same portion `id` → single event (`{"idempotent": true}`).

## 5. Matching & pricing rules (read before demoing)

**Matching = hard filter → rank → combine, never merge grades silently.**
Filters (fail any → excluded with reason): `herb_mismatch · unavailable · grade_below_required · harvest_too_old/too_new · missing_qr`. Rank survivors by visual_sim (experimental — photo similarity ≠ food safety) + date + delivery band + price fit. Different grades stay separate lines; mixed proposals set `mixed_grades:true`.

**Pricing = support tool, not market authority:** `Ctotal = Cprod+Cproc+Cpack+Ctrans+Cfees`, `Mkg = Psale−Ctotal`, `Mtotal = Q·Mkg`, warn if `Psale < Ctotal`. Only as accurate as entered costs; Phase 1 example (8.00+1.00+0.50+0.50=10.00, sale 12.00 → 2.00/kg, 20 kg → 40 DT) is illustrative until field validation.

## 6. Vision pipeline (deterministic, honest)

`capture` (fixed exposure, sensor trigger → `data/batches/<id>/img_<uuid>.jpg`) → `preprocess` (ROI crop, denoise, HSV green mask, largest contour; area/count gate → auto-`verify` on invalid) → `infer_onnx` (MobileNetV3-Small 224×224; heuristic greenness fallback if `.onnx` absent) → `decide` (confident-accepted + thresh → accepted; else Mode A `stop_alert` / Mode B `divert_verify`) → `serial_link` divert/stop + `PortionEvent` log. Train: `python -m vision.train` (LogisticRegression color+texture baseline in ~2 h; MobileNet finetune → ONNX is stretch). Eval: `python -m vision.eval` (held-out only — train accuracy is never reported as real).

## 7. Data — what counts and what doesn't

| Source | Path | License | Claim-grade? |
|---|---|---|---|
| Bench rosemary (REQUIRED 26–30 Oct, 400–800 imgs, 60/40, BY BATCH 70/15/15) | `data/raw/rosemary/{accepted,verify}/` | producer TEST, not redistributed | **YES — the ONLY numbers allowed in the report** |
| Wild rosemary presence (74 CC imgs, full attribution) | `data/external/inaturalist_rosemary/` | per-photo CC-BY/CC-BY-NC/CC-BY-SA/CC0, see `attribution.csv` | NO — pretraining/smoke only |
| Healthy/diseased analogy + built splits (73 pairs, deterministic blur/desat/rotate) | `data/surrogate/` + `manifest.csv` | CC-BY-SA-3.0 (PlantVillage, Hughes & Salamak 2015) | NO — pipeline smoke, labeled `claim_grade:false` |

No public post-harvest rosemary grade set exists (verified 23 Oct 2026 — see `data/DATASET_SOURCES.md`). Fetch: `make fetch-inat` → `make make-surrogate` → `make train-surrogate` → `make eval-surrogate`. Bench: `make train-bench` → `make eval-bench`. Full card: `data/dataset_card.md`.

## 8. Hardware (bench build, Phase 1)

Frame + 60–100 cm belt (DC gear motor 12 V 10–30 RPM PWM) · hopper + manual gate (15–25 g, gap ≥ 8 cm) · matte-black tunnel 30 cm + LED 5500 K diffused + fixed USB camera · servo flap (MG996R) + 2 chutes (accepted / verify) · IR break-beam at inspection exit · red/green LEDs · guards on belt sides + servo pinch point · mushroom e-stop (NC in series with motor PSU coil + sense line to MCU). Firmware: `hardware/firmware/src/main.cpp` (ESP32, JSONL 115200, modes A/B, jam/sensor/cover/estop faults, safe-boot motor OFF until resume + local button). Dust: hood + 120 mm 12 V fan + replaceable G4/F7 filter — reduces *some* visible dust, NOT respiratory protection. BOM 675–1,350 DT (~1,500 with laptop, excl. fabrication) is a planning list — 3 signed quotes + receipt photos required (`docs/bom_quotes.md`).

## 9. Repo map

```
app/            FastAPI + Jinja2 + HTMX, SQLite WAL, segno QR, pyserial
  routers/      batches | requests | orders | pricing | public (/b/) | station
  services/     matching | pricing | qr | serial_link (mock fallback) | vision_service (Mode A/B)
  templates/    index · producer · batch · station · buyer (+ public QR page)
vision/         capture · preprocess · train · infer_onnx · eval
hardware/       firmware/src/main.cpp (ESP32 JSONL, HW e-stop)
data/           raw/rosemary (bench, claim-grade) · external (CC surrogates) · surrogate (analogy splits) · batches/<id>/ (images+qr)
tests/          test_matching (T-M1..M7) · test_pricing · test_vision_logic · test_api_smoke · test_idempotency
scripts/        seed_demo · fetch_public_leaf_data · make_surrogate_splits · backup.sh
docs/           buyer_spec · bom_quotes · producer_notes · evidence/ · report/ (6-page .tex) · video/ (shotlist)
```

## 10. Docs & evidence index

- Locked spec: `docs/buyer_spec.md` (rosemary, 20 kg premium, 15–25 Oct window, Tunis, ≤14 DT/kg, QR required; accepted vs verify photo rule; 11+9 kg TEST fulfilment).
- Quotes: `docs/bom_quotes.md` (pending 3 signed quotes 24–27 Oct) · Interviews: `docs/producer_notes.md` (2–3 producers + 1–2 buyers, 15 min each).
- Evidence: `docs/evidence/matching_tests.md` (T-M1..M7 log) · `docs/evidence/surrogate_eval.json` (analogy, `claim_grade:false`) · `docs/evidence/eval_results.json` (bench, after 26–30 Oct).
- Report: `docs/report/main.tex` (Overleaf-ready IEEE, max 6 pp, anonymous) + `LAYOUT_AND_SETTINGS.md` + `OUTLINE.md` · Video: `docs/video/SHOTLIST.md` (3-min, 8 steps, anonymous, minimal edit).
- Dataset: `data/dataset_card.md` + `data/DATASET_SOURCES.md` + `data/external/README.md`.

## 11. Safety & limits (non-negotiable)

- Visual screening only. Cannot see moisture, contamination, chemicals, microbes, aroma. No food-safety certification.
- Low-confidence / overlap / blur / bad area → human verification. Accepted still may need moisture/hygiene/lab checks.
- E-stop cuts motor power in hardware. Software stop is NOT safety. Restart = deliberate local button + UI resume.
- Dust hood reduces some dust, NOT respiratory protection. Keep electronics sealed, clean filter per SOP.
- Prices/BOM illustrative until field validation. Surrogate metrics never presented as HER-GRADE accuracy.

## 12. Roadmap (13 days → 05 Nov)

- [x] P1 slice runnable: API + QR + matching + pricing + station + 16 tests + CI green
- [x] Surrogate data wired (74 CC rosemary + 73 analogy pairs + train/eval CLI + docs)
- [ ] Bench 400–800 photos 26–30 Oct (FINAL lighting) → `make train-bench` → `make eval-bench` → freeze numbers
- [ ] Bench proof: 20 portions no-jam, throughput/min, Mode A/B logs, e-stop 5×, dust before/after, 10/10 QR scans, 5 matching cases
- [ ] Field: producer/buyer interviews + 3 signed quotes + usability (2 prod + 1 buyer)
- [ ] Report: 6 pp original (Title/Abstract 150–250w/Keywords/Intro/Related/Methods/Results/Discussion/Conclusion/Refs), anonymous, no invented numbers
- [ ] Freeze + hand runnable 8-step demo to video team

## License

Code: **MIT** (see `LICENSE`). Images carry their own licenses: iNaturalist per-photo CC (see `data/external/inaturalist_rosemary/attribution.csv`); PlantVillage CC-BY-SA-3.0; bench photos all-rights-reserved TEST data, not for redistribution.
