# HER-GRADE 6-page report skeleton (Phase 1, Track 2 primary)
p1 — Title: HER-GRADE: Smart Herb Sorting, Traceability, Collective Marketing for Women Producers (rosemary pilot).
Abstract 150–250w: problem (small lots, sorting drudgery, no traceability, dust, intermediaries) → integration (conveyor visual-screening + 2-mode diverter + dust hood + batch QR + hard-filter matching + price tool) → methods (bench-fixed camera/LED, ≥300 rosemary images, 70/15/15 by batch, baseline→MobileNetV3-ONNX, val-tuned thresh, held-out eval) → results placeholders (acc, P/R, false-accept, review%, portions, throughput/min, dust before/after, 10/10 QR, matching 7/7, pricing vs costs, usability 2prod+1buyer) → limits (visual only, no moisture/chemical/microbe/aroma/food-safety).
Keywords: rosemary, visual inspection, traceability, collective marketing, women producers.
Intro: Track 2 + challenge sectors (essential-oil/agro-food) + 6 interconnections, field interviews summary.
p2 — Related work (manual sorting, marketplaces without screening, QR traceability) + Fig: system pipeline (10 steps).
p3 — HW: frame/hopper/belt/motor, tunnel+LED+camera, servo flap, IR, LEDs, HW e-stop (relay), guards; Electronics/firmware: ESP32 JSONL 115200, modes A/B, jam/sensor/cover/estop faults, safe-boot OFF.
p4 — SW: capture→preprocess→infer→decision→serial→log; matching hard-filter→rank→combine (never merge grades); pricing Ctotal/Mkg/Mtotal + below-cost warn. Results tables: dataset card, eval (acc/P/R/cm/latency), sorting counts, throughput, dust photos, QR 10/10, matching 7/7, pricing, usability.
p5 — Discussion: failures (overlap/jam/blur/threshold trade), limits (visual-only, dust≠respirator, prices illustrative), honesty notes.
p6 — Conclusion (Phase 1 slice runnable offline, what scales) + Future work ( Postgres, payments, multi-herb, field trial) + References (challenge PDF, OpenCV/ONNX/FastAPI/segno docs, MobileNetV3 paper).
Anonymity: no names/logos/uni/paths/voices/faces. Original prose (plagiarism incl. AI checked).
