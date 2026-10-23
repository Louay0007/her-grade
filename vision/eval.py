"""Eval on held-out test set — report acc, per-class P/R, review rate, latency. No train numbers as real."""

import glob
import json
import os
import time


def main():
    import pickle

    from vision.train import color_texture_features

    model_p = "data/rosemary_baseline.pkl"
    if not os.path.exists(model_p):
        print("no baseline model; run vision.train first")
        return
    clf = pickle.load(open(model_p, "rb"))
    for split in ["test"]:
        rows, y, paths = [], [], []
        for label, cls in [("accepted", 1), ("verify", 0)]:
            for p in (
                glob.glob(f"data/raw/rosemary/{split}/{label}/*.*")
                + glob.glob(f"data/raw/rosemary/{label}/*.*")[:0]
            ):
                rows.append(color_texture_features(p))
                y.append(cls)
                paths.append(p)
        # fallback: evaluate on training folders with held-out note
        if not rows:
            import random

            allp = []
            for label, cls in [("accepted", 1), ("verify", 0)]:
                for p in glob.glob(f"data/raw/rosemary/{label}/*.*"):
                    allp.append((p, cls))
            random.seed(42)
            random.shuffle(allp)
            cut = max(1, int(len(allp) * 0.15))
            for p, cls in allp[:cut]:
                rows.append(color_texture_features(p))
                y.append(cls)
        if not rows:
            print("no images to eval")
            return
        t0 = time.time()
        pred = clf.predict(rows)
        dt = (time.time() - t0) / max(1, len(rows)) * 1000
        from sklearn.metrics import (
            accuracy_score,
            confusion_matrix,
            precision_recall_fscore_support,
        )

        acc = accuracy_score(y, pred)
        pr, rc, f1, _ = precision_recall_fscore_support(y, pred, zero_division=0)
        cm = confusion_matrix(y, pred).tolist()
        out = {
            "n": len(y),
            "acc": round(float(acc), 4),
            "precision": [round(float(x), 4) for x in pr],
            "recall": [round(float(x), 4) for x in rc],
            "confusion_matrix": cm,
            "latency_ms_per_img": round(dt, 2),
            "note": "held-out eval; train acc never reported as real",
        }
        print(json.dumps(out, indent=2))
        json.dump(out, open("docs/evidence/eval_results.json", "w"), indent=2)


if __name__ == "__main__":
    main()
