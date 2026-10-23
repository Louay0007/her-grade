# Dataset card — rosemary visual-screening (Phase 1)
- Herb LOCKED: rosemary only. No mixed herb piles.
- Location: `data/raw/rosemary/{accepted,verify}/` (+ `test/` holdout when collected).
- Capture: fixed USB camera, 1280x720, locked exposure, LED 5500K diffused, 30s warmup, contrasting dark belt, height fixed.
- Labels: accepted-looking = green intact needles, no yellowing/stems/dust clumps; verify = yellowed, stemmy, dusty, foreign matter, overlap, blur. Two reviewers for borderline.
- Split BY BATCH: train 70 / val 15 / test 15 unseen. Test never touches train.
- Status P1-start: 0 images collected — bench collection 26-30 Oct per plan. Threshold v0.1-0.75 initial, MUST calibrate on val (target <5% false-accept).
- License/consent: producer-taken bench photos, TEST only, no faces/names.
