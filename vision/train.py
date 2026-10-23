"""Train: baseline LogisticRegression on color+texture (2h) then MobileNetV3-Small finetune -> ONNX.
Usage: python -m vision.train --data data/raw/rosemary --out data/rosemary_mobilenetv3.onnx
Phase 1: if torch unavailable, trains sklearn baseline and exports threshold card only.
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/rosemary")
    ap.add_argument("--out", default="data/rosemary_mobilenetv3.onnx")
    args = ap.parse_args()
    rows, y = [], []
    for label, cls in [("accepted", 1), ("verify", 0)]:
        d = os.path.join(args.data, label)
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                try:
                    rows.append(color_texture_features(os.path.join(d, f)))
                    y.append(cls)
                except Exception as e:
                    print("skip", f, e)
    if len(rows) < 10:
        print(
            f"NOT ENOUGH DATA: {len(rows)} images. Collect >=300 per plan. Wrote threshold card only."
        )
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        json.dump(
            {"thresh": 0.75, "n": len(rows), "note": "insufficient data"},
            open("data/thresh_card.json", "w"),
        )
        return
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    from sklearn.model_selection import train_test_split

    X = np.array(rows)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)
    clf = LogisticRegression(max_iter=1000)
    clf.fit(Xtr, ytr)
    pred = clf.predict(Xte)
    acc = accuracy_score(yte, pred)
    pr, rc, f1, _ = precision_recall_fscore_support(yte, pred, zero_division=0)
    print(f"baseline held-out acc={acc:.3f} prec={pr} rec={rc}")
    import pickle

    pickle.dump(clf, open("data/rosemary_baseline.pkl", "wb"))
    json.dump({"thresh": 0.75, "acc": acc, "n": len(rows)}, open("data/thresh_card.json", "w"))
    print("saved baseline + thresh card. MobileNet finetune = Phase 1 stretch (see plan §5).")


if __name__ == "__main__":
    main()
