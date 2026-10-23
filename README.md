# HER-GRADE — Smart Herb Sorting, Traceability & Collective Marketing

**Track 2** — Supply Chain Fragmentation & Limited Direct Market Access (support: Track 1, Track 3).
**Phase 1 deadline:** 05 Nov 2026. **Status:** fixed idea, 13-day build.

Low-cost conveyor visual-inspection station + dust extraction + batch QR + collective marketplace for women herb producers. Fully self-hosted, works offline on one laptop.

## Quickstart (offline-capable)
```bash
cp .env.example .env
docker compose up --build -d
# local:  http://localhost:8000
# LAN (phone QR scan): http://<laptop-lan-ip>:8080
```
Dev without docker:
```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Demo accounts (TEST data only)
- producer1 / test, producer2 / test, buyer1 / test

## 8-step jury demo
1. Producer creates batch (rosemary, harvest date, locality).
2. Feed portions -> accepted / verify divert (Mode B).
3. Mode A: uncertain -> red alert + stop, operator resumes.
4. Finish batch -> QR -> phone scans `/b/<id>`.
5. Buyer requests 20kg grade X.
6. System proposes 11kg + 9kg collective, scores explained.
7. Each producer accepts, buyer confirms. Mixed grades never merged silently.
8. Price calculator with below-cost warning (illustrative).

## Repo map
- `app/` FastAPI + Jinja2 + HTMX, SQLite WAL, pyserial, segno QR
- `vision/` OpenCV capture/preprocess, MobileNetV3-Small ONNX, eval
- `hardware/` ESP32 firmware, wiring, BOM, safety checklist
- `tests/` matching/pricing/API/idempotency — must pass before freeze
- `docs/` buyer spec, evidence logs, report outline, video shotlist
- `scripts/` demo seed, backup, dev runners

## Safety & honesty
- Camera = visual screening only. No food-safety claim.
- E-stop cuts motor power in hardware. Software stop is NOT safety.
- All prices/BOM = planning estimates until field quotes. Never present as market truth.
