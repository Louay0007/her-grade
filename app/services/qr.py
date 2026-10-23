"""QR service — segno local generation. QR links to /b/<batch_id> only."""

import os

import segno


def batch_url(batch_id: str, base_url: str) -> str:
    return f"{base_url.rstrip('/')}/b/{batch_id}"


def make_qr(batch_id: str, base_url: str, out_dir: str = "./data/batches") -> dict:
    url = batch_url(batch_id, base_url)
    d = os.path.join(out_dir, batch_id)
    os.makedirs(d, exist_ok=True)
    png_path = os.path.join(d, "qr.png")
    qr = segno.make(url, micro=False)
    qr.save(png_path, scale=6, border=2)
    return {"url": url, "png": png_path}
