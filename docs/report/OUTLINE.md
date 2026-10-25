# HER-GRADE 6-page report — section plan (IEEE conference, max 6 pp, anonymous, original prose)

p1 — Title: HER-GRADE: Smart Herb Sorting, Traceability, Collective Marketing for Women Producers (rosemary pilot).
Abstract 150–250 words: problem (small lots below buyer minimums, sorting drudgery, no traceability, dust, intermediaries) → integration (conveyor visual-screening + 2-mode diverter + dust hood + batch QR + hard-filter matching + price tool) → methods (bench-fixed camera/LED, ≥300 rosemary images, BY-BATCH 70/15/15, baseline→MobileNetV3-ONNX, val-tuned threshold, held-out eval) → results (acc, P/R, false-accept, review%, portions, throughput/min, dust before/after, 10/10 QR, matching 7/7, pricing vs costs, usability 2+1) → limits (visual only; no moisture/chemical/microbe/aroma/food-safety).
Keywords (3–6): rosemary, visual inspection, traceability, collective marketing, women producers.
Intro: Track 2 primary + challenge sectors (essential-oil distillation, agro-food processing) + 6 interconnections; field interviews summary.

p2 — Related work (manual sorting benches, marketplaces without screening, QR traceability pilots) + Figure: 10-step system pipeline.

p3 — Hardware + firmware: frame/hopper/belt/motor, tunnel + LED + camera, servo flap + chutes, IR sensor, LEDs, HW e-stop relay + guards; ESP32 JSONL 115200, modes A/B, jam/sensor/cover/estop faults, heartbeat, safe-boot OFF.

p4 — Software + matching + pricing: capture→preprocess→infer→decide→serial→log; hard-filter→rank→combine (grades never merged silently); Ctotal/Mkg/Mtotal + below-cost warn. Results tables: dataset card, held-out eval (acc/P/R/CM/latency), sorting counts, throughput, dust photos, QR 10/10, matching 7/7, pricing, usability.

p5 — Discussion: failures (overlap/jam/blur/threshold trade), limits (visual-only, dust≠respirator, surrogate≠claim, prices illustrative), honesty notes, threats to validity.

p6 — Conclusion (offline Phase 1 slice, what scales to field) + Future work (Postgres, payments, multi-herb, field trial, MobileNet finetune) + References + Acknowledgments (anonymous). Full text: `docs/report/main.tex`.
