"""Train baseline LogisticRegression on color+texture; MobileNet finetune = stretch.
Usage:
  python -m vision.train --data data/raw/rosemary --out data/rosemary_baseline.pkl
  python -m vision.train --data data/surrogate/train --out data/surrogate_baseline.pkl --thresh-out data/surrogate_thresh.json
Bench data (data/raw/rosemary) is the ONLY claim-grade source. Surrogate runs are pipeline smoke only.
"""

import argparse
import json
import os


def color_texture_features(image_path: str):
    import numpy as np
    from PIL import Image

    img = Image.open(image_path).convert("RGB").resize((128, 128))
    a = np.asarray(img).astype(float) / 255.0
    hsv = None
    try:
        import cv2

        bgr = cv2.cvtColor((a * 255).astype("uint8"), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).mean(axis=(0, 1)) / 255.0
    except Exception:
        hsv = np.array([0.3, 0.4, 0.4])
    rgb_mean = a.mean(axis=(0, 1))
    rgb_std = a.std(axis=(0, 1))
    return list(rgb_mean) + list(rgb_std) + list(hsv)


def load_split(data_dir):
    rows, y = [], []
    for label, cls in [("accepted", 1), ("verify", 0)]:
        d = os.path.join(data_dir, label)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                try:
                    rows.append(color_texture_features(os.path.join(d, f)))
                    y.append(cls)
                except Exception as e:
                    print("skip", f, str(e)[:80])
    return rows, y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/rosemary")
    ap.add_argument("--out", default="data/rosemary_baseline.pkl")
    ap.add_argument("--thresh-out", default="data/thresh_card.json")
    ap.add_argument("--val-ratio", type=float, default=0.15)
    args = ap.parse_args()
    rows, y = load_split(args.data)
    claim_grade = os.path.abspath(args.data).rstrip("/").endswith("data/raw/rosemary")
    if len(rows) < 10:
        print(f"NOT ENOUGH DATA: {len(rows)} images in {args.data}.")
        print("Bench: collect >=300 per plan. Surrogate: run make_surrogate first.")
        os.makedirs(os.path.dirname(os.path.abspath(args.thresh_out)) or ".", exist_ok=True)
        with open(args.thresh_out, "w") as f:
            json.dump({"thresh": 0.75, "n": len(rows), "note": "insufficient data"}, f)
        return
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    from sklearn.model_selection import train_test_split

    X = np.array(rows)
    Xtr, Xva, ytr, yva = train_test_split(
        X, y, test_size=args.val_ratio, random_state=42, stratify=y
    )
    clf = LogisticRegression(max_iter=1000)
    clf.fit(Xtr, ytr)
    pred = clf.predict(Xva)
    acc = accuracy_score(yva, pred)
    pr, rc, _f1, _ = precision_recall_fscore_support(yva, pred, zero_division=0)
    print(f"val acc={acc:.3f} prec={list(pr)} rec={list(rc)} n={len(y)} ({args.data})")
    import pickle

    with open(args.out, "wb") as f:
        pickle.dump(clf, f)
    with open(args.thresh_out, "w") as f:
        json.dump(
            {
                "thresh": 0.75,
                "acc": round(float(acc), 4),
                "n": len(rows),
                "claim_grade": claim_grade,
                "note": "bench held-out ONLY is claim-grade; surrogate = pipeline smoke",
            },
            f,
        )
    print(f"saved {args.out} + {args.thresh_out}. MobileNet finetune = stretch (plan 5).")


if __name__ == "__main__":
    main()
