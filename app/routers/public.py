"""Public QR page /b/<batch_id> — approved info only, no contacts/price."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from .. import models
from ..db import get_db

router = APIRouter()


@router.get("/b/{bid}", response_class=HTMLResponse)
def public_batch(bid: str, db: Session = Depends(get_db)):
    b = db.get(models.Batch, bid)
    if not b:
        raise HTTPException(404, "unknown batch")
    prod = db.get(models.Producer, b.producer_id)
    evts = db.query(models.PortionEvent).filter_by(batch_id=bid).all()
    acc = sum(1 for e in evts if e.target == "accepted")
    ver = sum(1 for e in evts if e.target == "verify")
    return f"""<!doctype html><html><head><meta charset=utf-8>
<meta name=viewport content='width=device-width,initial-scale=1'>
<title>HER-GRADE batch {b.id}</title>
<style>body{{font-family:system-ui;max-width:640px;margin:24px auto;padding:0 16px}}
.card{{border:1px solid #ccc;border-radius:12px;padding:16px;margin:12px 0}}
.mut{{color:#555;font-size:13px}}</style></head><body>
<h2>HER-GRADE — traceability</h2>
<div class=card><b>Herb:</b> {b.herb_type}<br>
<b>Batch:</b> {b.id}<br>
<b>Harvest date (as entered):</b> {b.harvest_date}<br>
<b>Locality (level):</b> {b.locality}<br>
<b>Grade:</b> {b.grade} (visual screening only — not food-safety certified)<br>
<b>Qty:</b> accepted-looking {b.accepted_g}g / verification {b.verify_g}g / total {b.total_g}g<br>
<b>Producer:</b> {prod.display_name if prod else '?'}<br>
<b>Portions:</b> {len(evts)} (accepted {acc} / verify {ver})<br>
<b>Threshold:</b> {b.thresh_version}</div>
<p class=mut>Camera = visual screening only. Cannot detect moisture, chemicals, microbes, aroma. Low-confidence portions go to human verification.</p>
</body></html>"""
