"""Build accepted/verify ANALOGY splits from surrogates for pipeline testing (NOT claim-grade).
- accepted ANALOGY: green-dominant images (inat rosemary + PV healthy) resized 224.
- verify ANALOGY: yellow/brown/dark + blur/overlap synthetics from same pool (documented transforms).
Outputs data/surrogate/{train,val,test}/{accepted,verify}/ + manifest.csv
NEVER present surrogate metrics as HER-GRADE accuracy. Bench eval only.
"""

import csv
import os
import random

random.seed(42)


def collect(pool_dirs):
    files = []
    for d in pool_dirs:
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.lower().endswith((".jpg", ".jpeg", ".png")):
                    files.append(os.path.join(d, f))
    return sorted(files)


def main():
    from PIL import Image, ImageEnhance, ImageFilter

    inat = collect(["data/external/inaturalist_rosemary/images"])
    pv_acc = collect(["data/external/plantvillage_subset/accepted"])
    pv_ver = collect(["data/external/plantvillage_subset/verify"])
    pool = inat + pv_acc + pv_ver
    if len(pool) < 20:
        print(
            f"surrogate pool too small ({len(pool)}). Run fetch script first; bench still required."
        )
        return
    random.shuffle(pool)
    n = len(pool)
    splits = {
        "train": pool[: int(n * 0.7)],
        "val": pool[int(n * 0.7) : int(n * 0.85)],
        "test": pool[int(n * 0.85) :],
    }
    rows = []
    for split, files in splits.items():
        for i, src in enumerate(files):
            try:
                img = Image.open(src).convert("RGB").resize((224, 224))
            except Exception as e:
                print("skip", src, e)
                continue
            # accepted analogy: as-is green crop; verify analogy: deterministic transform rotation
            acc_p = f"data/surrogate/{split}/accepted/surr_{i:04d}.jpg"
            ver_p = f"data/surrogate/{split}/verify/surr_{i:04d}.jpg"
            os.makedirs(os.path.dirname(acc_p), exist_ok=True)
            os.makedirs(os.path.dirname(ver_p), exist_ok=True)
            img.save(acc_p)
            v = img.filter(ImageFilter.GaussianBlur(3 if i % 3 == 0 else 1))
            v = ImageEnhance.Color(v).enhance(0.5)
            v = ImageEnhance.Brightness(v).enhance(1.15)
            if i % 2 == 0:
                v = v.rotate(25, expand=False)
            v.save(ver_p)
            rows.append({"split": split, "accepted": acc_p, "verify": ver_p, "src": src})
    os.makedirs("data/surrogate", exist_ok=True)
    with open("data/surrogate/manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["split", "accepted", "verify", "src"])
        w.writeheader()
        w.writerows(rows)
    print(f"surrogate splits: {len(rows)} pairs -> data/surrogate/ (ANALOGY ONLY, not claim-grade)")


if __name__ == "__main__":
    main()
