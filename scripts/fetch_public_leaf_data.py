"""Fetch public surrogate leaf data for HER-GRADE bench pretraining + eval harness.
Strategy (documented, honest):
  - NO public dataset exists for "rosemary accepted vs needs-verification" post-harvest grading.
  - Bench photos under FINAL lighting remain REQUIRED (plan Phase 4). This script fetches
    LICENSED surrogates for pipeline testing + backbone pretraining ONLY:
    A) iNaturalist research-grade Salvia rosmarinus photos (CC-BY/CC-BY-NC, attribution CSV).
    B) PlantVillage subset (healthy vs diseased leaves) for accepted/verify ANALOGY training.
Surrogates NEVER replace bench eval numbers in the 6-page report. Held-out bench eval is the only
claim-grade evidence. See data/DATASET_SOURCES.md.
Usage:
  python scripts/fetch_public_leaf_data.py --source inat --n 800
  python scripts/fetch_public_leaf_data.py --source plantvillage --n 800
"""

import argparse
import csv
import json
import os
import time
import urllib.request

INAT_TAXON = 636795  # Salvia rosmarinus
OUT_INAT = "data/external/inaturalist_rosemary"
OUT_PV = "data/external/plantvillage_subset"


def dl(url, path, timeout=30):
    try:
        urllib.request.urlretrieve(url, path)
        return True
    except Exception as e:
        print("skip", url[:80], str(e)[:100])
        return False


def fetch_inat(n=800, per_page=100):
    os.makedirs(f"{OUT_INAT}/images", exist_ok=True)
    got, page, rows = 0, 1, []
    while got < n and page <= 30:
        api = (
            f"https://api.inaturalist.org/v1/observations?taxon_id={INAT_TAXON}"
            f"&photos=true&quality_grade=research&photo_license=cc-by,cc-by-nc,cc-by-sa,cc0&per_page={per_page}&page={page}&order=desc&order_by=created_at"
        )
        try:
            with urllib.request.urlopen(api, timeout=30) as r:
                d = json.load(r)
        except Exception as e:
            print("inat api err", e)
            break
        results = d.get("results", [])
        if not results:
            break
        for o in results:
            if got >= n:
                break
            lic = (o.get("license_code") or "").lower()
            if lic not in ("cc-by", "cc-by-nc", "cc-by-sa", "cc0"):
                continue  # licensed only, attribution kept
            photos = o.get("photos", [])
            if not photos:
                continue
            pid = o.get("id")
            u = (photos[0].get("url") or "").replace("square.", "large.")
            if not u:
                continue
            fn = f"inat_{pid}.jpg"
            if dl(u, f"{OUT_INAT}/images/{fn}"):
                rows.append(
                    {
                        "file": fn,
                        "inat_id": pid,
                        "license": lic,
                        "observer": (o.get("user") or {}).get("login", ""),
                        "observed_on": o.get("observed_on") or "",
                        "place": (o.get("place_guess") or "")[:80],
                        "url": f"https://www.inaturalist.org/observations/{pid}",
                    }
                )
                got += 1
        print(f"inat page {page}: got {got}/{n}")
        page += 1
        time.sleep(1)
    with open(f"{OUT_INAT}/attribution.csv", "w", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["file", "inat_id", "license", "observer", "observed_on", "place", "url"]
        )
        w.writeheader()
        w.writerows(rows)
    print(f"inat done: {got} images -> {OUT_INAT}/images + attribution.csv")


def fetch_plantvillage(n=800):
    # Kaggle-free mirror via HF parquet (mohanty/PlantVillage). Needs `datasets` lib; else manual.
    try:
        from datasets import load_dataset
    except ImportError:
        print("pip install 'datasets pyarrow' then re-run --source plantvillage")
        print(
            "manual fallback: https://www.kaggle.com/datasets/emmarex/plantdisease (CC-BY-SA-3.0 Hughes&Salam 2015)"
        )
        return
    os.makedirs(f"{OUT_PV}/accepted", exist_ok=True)
    os.makedirs(f"{OUT_PV}/verify", exist_ok=True)
    ds = load_dataset("mohanty/PlantVillage", split="train", streaming=True)
    acc = ver = 0
    target_each = n // 2
    for i, ex in enumerate(ds):
        label = str(ex.get("label", "")).lower()
        img = ex.get("image")
        healthy = "healthy" in label
        if healthy and acc >= target_each:
            continue
        if not healthy and ver >= target_each:
            continue
        sub = "accepted" if healthy else "verify"
        try:
            img.save(f"{OUT_PV}/{sub}/pv_{i:05d}.jpg")
            if healthy:
                acc += 1
            else:
                ver += 1
        except Exception as e:
            print("skip pv", i, str(e)[:80])
        if acc >= target_each and ver >= target_each:
            break
        if i % 500 == 0:
            print(f"pv scanned {i}: acc {acc} ver {ver}")
    print(f"pv done: accepted {acc} verify {ver} -> {OUT_PV}/")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["inat", "plantvillage", "all"], default="inat")
    ap.add_argument("--n", type=int, default=800)
    a = ap.parse_args()
    if a.source in ("inat", "all"):
        fetch_inat(a.n)
    if a.source in ("plantvillage", "all"):
        fetch_plantvillage(a.n)
