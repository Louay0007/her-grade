# HER-GRADE data sources — surrogate + bench (honest provenance)

## Finding (23 Oct 2026, web search)
**No public dataset exists for post-harvest rosemary "accepted vs needs-verification" grading.**
Searched HuggingFace (rosemary / herb / medicinal / leaf / spice / food-quality): closest hits are
species-ID sets, NOT grade sets:
- `SimonWJ/Herb163CMR` — 163 Chinese-herb species ID (retrieval, no license, no rosemary grade).
- `Project-AgML/DIMPSAR_medicinal_leaf_classification` — 6,900 imgs / 80 species ID (CC-BY-4.0) — species, not grade.
- `enalis/LeafNet` — 186k leaf-disease (CC-BY-4.0) — disease analogy only.
- `mohanty/PlantVillage` — 54k healthy-vs-diseased leaves (CC-BY-SA-3.0, Hughes & Salamak 2015).
- iNaturalist `Salvia rosmarinus` taxon 636795 — ~17.9k research-grade wild-plant photos (mixed CC licenses).

## What we use (and what we DON'T claim)
| Source | Use | License | Claim-grade? |
|---|---|---|---|
| `data/external/inaturalist_rosemary/` | backbone pretraining + pipeline smoke test (species presence) | per-photo CC-BY/CC-BY-NC/CC-BY-SA/CC0, see `attribution.csv` | NEVER — wild plants ≠ bench grading |
| `data/external/plantvillage_subset/` | healthy-vs-diseased ANALOGY for accepted/verify pipeline test | CC-BY-SA-3.0 (cite Hughes & Salamak 2015) | NEVER — analogy only |
| `data/raw/rosemary/{accepted,verify}/` | **bench photos under FINAL lighting — REQUIRED 26–30 Oct** | producer-taken, TEST only | ONLY claim-grade eval source |

## Bench protocol (REQUIRED, Phase 4)
- Fixed USB camera 1280x720, locked exposure, LED 5500K diffused, 30s warmup, dark contrasting belt, fixed height.
- 400–800 portions: 60% accepted (green intact), 40% verify (yellowed/stemmy/dusty/foreign/overlap/blur).
- Label with producer/expert, two reviewers for borderline. Split BY BATCH 70/15/15, test unseen + locked.
- Bench eval (`vision/eval.py`) on held-out test is the ONLY number allowed in the 6-page report.

## Reproduce
```bash
python scripts/fetch_public_leaf_data.py --source inat --n 800        # licensed rosemary presence
python scripts/fetch_public_leaf_data.py --source plantvillage --n 800 # healthy/diseased analogy
python -m vision.train --data data/raw/rosemary --out data/rosemary_mobilenetv3.onnx
python -m vision.eval   # held-out bench only
```
