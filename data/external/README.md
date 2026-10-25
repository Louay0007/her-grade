# External surrogate data — NOT claim-grade (do not cite as HER-GRADE accuracy)

## What is here
- `inaturalist_rosemary/images/` — 74 wild *Salvia rosmarinus* photos (taxon 636795), CC-licensed research-grade observations. Per-photo license + observer + source URL in `attribution.csv` (licenses observed: CC-BY-NC ×55, CC-BY ×4, remainder `see-page` = verify on the linked observation before reuse).
- `plantvillage_subset/` — reserved for the healthy-vs-diseased analogy fetch (CC-BY-SA-3.0, Hughes & Salamak 2015). Empty until `make fetch-pv` is run.

## Allowed uses
- Backbone pretraining and pipeline smoke tests only (capture → preprocess → train → eval harness runs end-to-end).
- Verify-analogy splits in `data/surrogate/` are deterministic transforms (blur/desaturate/rotate), NOT real defects.

## Forbidden
- Never report surrogate accuracy, precision, recall, or latency as HER-GRADE results in the 6-page report, video, or judging Q&A.
- Claim-grade numbers come ONLY from bench photos under FINAL lighting: `data/raw/rosemary/` evaluated with `make eval-bench` → `docs/evidence/eval_results.json`.

## Reproduce
```bash
make fetch-inat        # licensed rosemary presence set + attribution.csv
make make-surrogate    # 70/15/15 analogy splits + manifest.csv
make train-surrogate && make eval-surrogate   # smoke only, claim_grade:false
```
