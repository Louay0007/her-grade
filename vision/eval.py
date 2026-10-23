"""Eval on held-out test — acc, per-class P/R, review rate, latency.
Claim-grade ONLY on bench: --data data/raw/rosemary. Surrogate: --data data/surrogate/test (labeled ANALOGY).
"""

import argparse
import glob
import json
import os
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/rosemary")
    ap.add_argument("--model", default="data/rosemary_baseline.pkl")
    ap.add_argument("--out", default="docs/evidence/eval_results.json")
    ap.add_argument("--thresh", type=float, default=0.75)
    args = ap.parse_args()
    import pickle

    from vision.train import color_texture_features

    if not os.path.exists(args.model):
        print(f"no model {args.model}; run vision.train first")
        return
    with open(args.model, "rb") as f:
        clf = pickle.load(f)
    rows, y = [], []
    for label, cls in [("accepted", 1), ("verify", 0)]:
        for p in (
            sorted(glob.glob(f"{args.data}/test/{label}/*.*"))
            + sorted(glob.glob(f"{args.data}/{label}/*.*"))[:0]
        ):
            rows.append(color_texture_features(p))
            y.append(cls)
    if not rows:  # bench fallback: random 15% holdout from flat folders
        import random

        allp = []
        for label, cls in [("accepted", 1), ("verify", 0)]:
            for p in sorted(glob.glob(f"{args.data}/{label}/*.*")):
                allp.append((p, cls))
        random.seed(42)
        random.shuffle(allp)
        cut = max(1, int(len(allp) * 0.15))
        for p, cls in allp[:cut]:
            rows.append(color_texture_features(p))
            y.append(cls)
    if not rows:
        print(f"no images in {args.data}")
        return
    t0 = time.time()
    proba = clf.predict_proba(rows)[:, 1] if hasattr(clf, "predict_proba") else clf.predict(rows)
    pred = [1 if p >= args.thresh else 0 for p in proba]
    dt = (time.time() - t0) / max(1, len(rows)) * 1000
    from sklearn.metrics import (
        accuracy_score,
        confusion_matrix,
        precision_recall_fscore_support,
    )

    acc = accuracy_score(y, pred)
    pr, rc, _f1, _ = precision_recall_fscore_support(y, pred, zero_division=0)
    cm = confusion_matrix(y, pred).tolist()
    claim = os.path.abspath(args.data).rstrip("/").endswith("data/raw/rosemary")
    out = {
        "data": args.data,
        "model": args.model,
        "n": len(y),
        "thresh": args.thresh,
        "acc": round(float(acc), 4),
        "precision": [round(float(x), 4) for x in pr],
        "recall": [round(float(x), 4) for x in rc],
        "confusion_matrix": cm,
        "false_accept_rate": round(float(cm[0][1] / max(1, sum(cm[0]))), 4) if len(cm) == 2 else 0,
        "review_rate": round(float(sum(1 for p in pred if p == 0) / max(1, len(pred))), 4),
        "latency_ms_per_img": round(dt, 2),
        "claim_grade": claim,
        "note": "ONLY bench held-out is claim-grade; surrogate labeled ANALOGY",
    }
    print(json.dumps(out, indent=2))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
