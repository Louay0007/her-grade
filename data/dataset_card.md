# Dataset card — rosemary visual-screening (Phase 1)
**Herb LOCKED:** rosemary only · **Track:** Track 2 primary (support Track 1+3) · **Updated:** 2026-10-23

## Claim-grade source (ONLY numbers allowed in report)
- Location: `data/raw/rosemary/{accepted,verify}/` (+ `test/` holdout when collected).
- Capture: fixed USB camera 1280x720, locked exposure, LED 5500K diffused, 30s warmup, dark contrasting belt, fixed height. No phone pics.
- Labels: accepted-looking = green intact needles, uniform green, no yellowing/stems/dust/foreign; verify = yellowed/stemmy/dusty/foreign/overlap/blur/area-invalid/conf < thresh. Two reviewers for borderline.
- Split BY BATCH: train 70 / val 15 / test 15 unseen. Test never touches train. `python -m vision.eval --data data/raw/rosemary` is the ONLY claim-grade eval.
- Status: **0 bench images — collect 400–800 26–30 Oct** (60% accepted / 40% verify). Threshold v0.1-0.75 initial, calibrate on val (target <5% false-accept).
- License/consent: producer-taken bench photos, TEST only, no faces/names/paths.

## Surrogate sources (pipeline smoke + pretraining ONLY — NEVER claim-grade)
Finding 23-Oct-2026: **no public post-harvest rosemary grade set exists.** Closest licensed stand-ins:
1. **iNaturalist `Salvia rosmarinus` (taxon 636795)** — ~13k CC-licensed research-grade wild photos.
   Local: `data/external/inaturalist_rosemary/images/` + `attribution.csv` (per-photo CC-BY/CC-BY-NC/CC-BY-SA/CC0, observer, URL).
   Fetch: `python scripts/fetch_public_leaf_data.py --source inat --n 800`. Use: backbone pretraining + smoke only (wild ≠ bench grading).
2. **PlantVillage healthy-vs-diseased analogy** (Hughes & Salamak 2015, CC-BY-SA-3.0) — `data/external/plantvillage_subset/{accepted,verify}/`.
   Fetch: `python scripts/fetch_public_leaf_data.py --source plantvillage --n 800`. Use: accepted/verify ANALOGY pipeline test only.
3. **Built surrogate splits** — `data/surrogate/{train,val,test}/{accepted,verify}/` + `manifest.csv` via `python scripts/make_surrogate_splits.py`.
   Verify-analogy = deterministic blur/desaturate/rotate of same pool (documented, NOT real defects).
   Eval: `python -m vision.eval --data data/surrogate/test --model data/surrogate_baseline.pkl --out docs/evidence/surrogate_eval.json` → labeled `"claim_grade": false`.

## Reproduce
```bash
python scripts/fetch_public_leaf_data.py --source inat --n 800
python scripts/make_surrogate_splits.py
python -m vision.train --data data/surrogate/train --out data/surrogate_baseline.pkl --thresh-out data/surrogate_thresh.json
python -m vision.eval --data data/surrogate/test --model data/surrogate_baseline.pkl --out docs/evidence/surrogate_eval.json
# BENCH (claim-grade, after 26–30 Oct collection):
python -m vision.train --data data/raw/rosemary --out data/rosemary_baseline.pkl
python -m vision.eval --data data/raw/rosemary --out docs/evidence/eval_results.json
```
See also: `data/DATASET_SOURCES.md` (full provenance + decision), `data/external/README.md`.
