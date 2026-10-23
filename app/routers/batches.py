"""Batches: create -> portions (vision decision + serial divert) -> finish (QR)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import settings
from ..db import get_db
from ..services import qr as qr_svc
from ..services.serial_link import get_link
from ..services.vision_service import decide

router = APIRouter()
PORTION_G = 20  # grams per portion (Phase 1 fixed, scale-validated)


@router.post("")
def create_batch(body: schemas.BatchCreate, db: Session = Depends(get_db)):
    prod = db.get(models.Producer, body.producer_id)
    if not prod:
        raise HTTPException(404, f"producer {body.producer_id} not found (seed demo first)")
    b = models.Batch(
        producer_id=body.producer_id,
        herb_type="rosemary",
        harvest_date=body.harvest_date,
        locality=body.locality,
        grade=body.grade,
        avail_g=0,
        unit_ask=body.unit_ask,
        status="open",
        thresh_version=settings.thresh_version,
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return {"id": b.id, "herb_type": b.herb_type, "status": b.status, "grade": b.grade}


@router.get("")
def list_batches(db: Session = Depends(get_db)):
    return [
        {
            "id": b.id,
            "producer_id": b.producer_id,
            "herb_type": b.herb_type,
            "grade": b.grade,
            "total_g": b.total_g,
            "accepted_g": b.accepted_g,
            "verify_g": b.verify_g,
            "avail_g": b.avail_g,
            "status": b.status,
            "qr_id": b.qr_id,
        }
        for b in db.query(models.Batch).all()
    ]


@router.get("/{bid}")
def get_batch(bid: str, db: Session = Depends(get_db)):
    b = db.get(models.Batch, bid)
    if not b:
        raise HTTPException(404, "batch not found")
    evts = db.query(models.PortionEvent).filter_by(batch_id=bid).all()
    return {
        "id": b.id,
        "producer_id": b.producer_id,
        "herb_type": b.herb_type,
        "harvest_date": b.harvest_date,
        "locality": b.locality,
        "grade": b.grade,
        "total_g": b.total_g,
        "accepted_g": b.accepted_g,
        "verify_g": b.verify_g,
        "avail_g": b.avail_g,
        "status": b.status,
        "qr_id": b.qr_id,
        "thresh_version": b.thresh_version,
        "mode": b.mode,
        "portions": len(evts),
    }


@router.post("/{bid}/portions")
def add_portion(
    bid: str,
    body: schemas.PortionIn,
    mode: str = Query(default="B", pattern="^(A|B)$"),
    db: Session = Depends(get_db),
):
    b = db.get(models.Batch, bid)
    if not b:
        raise HTTPException(404, "batch not found")
    if b.status == "finished":
        raise HTTPException(409, "batch already finished")
    evt_id = body.id or f"evt-{uuid.uuid4().hex[:12]}"
    existing = db.get(models.PortionEvent, evt_id)
    if existing:
        return {"idempotent": True, "id": existing.id, "target": existing.target}
    try:
        thresh = float(settings.thresh_version.split("-")[-1])
    except Exception:
        thresh = 0.75
    d = decide(
        body.pred,
        body.conf,
        thresh=thresh,
        mode=mode,
        area_ok=body.area_ok,
        overlap=body.overlap,
    )
    target = d["target"]  # accepted | verify
    link = get_link(settings.serial_port, settings.serial_baud)
    if d["action"] == "stop_alert":
        link.stop(d["reason"])
        link._send({"t": "alert", "level": "red", "reason": d["reason"]})
    else:
        link.divert(evt_id, target)
    evt = models.PortionEvent(
        id=evt_id,
        batch_id=bid,
        image_ref=body.image_ref,
        pred=body.pred,
        conf=body.conf,
        target=target,
        thresh_version=settings.thresh_version,
    )
    db.add(evt)
    b.total_g += PORTION_G
    if target == "accepted":
        b.accepted_g += PORTION_G
    else:
        b.verify_g += PORTION_G
    b.mode = mode
    db.commit()
    return {
        "id": evt_id,
        "target": target,
        "action": d["action"],
        "reason": d["reason"],
        "total_g": b.total_g,
        "accepted_g": b.accepted_g,
        "verify_g": b.verify_g,
    }


@router.post("/{bid}/finish")
def finish_batch(bid: str, db: Session = Depends(get_db)):
    from ..config import settings as s

    b = db.get(models.Batch, bid)
    if not b:
        raise HTTPException(404, "batch not found")
    b.avail_g = b.accepted_g  # only accepted-looking grams are sellable
    b.status = "published"
    b.qr_id = b.id
    base = s.app_base_url
    out = qr_svc.make_qr(b.id, base)
    db.commit()
    return {
        "id": b.id,
        "qr_url": out["url"],
        "qr_png": out["png"],
        "total_g": b.total_g,
        "accepted_g": b.accepted_g,
        "verify_g": b.verify_g,
        "avail_g": b.avail_g,
        "status": b.status,
    }


@router.get("/{bid}/events")
def batch_events(bid: str, db: Session = Depends(get_db)):
    evts = db.query(models.PortionEvent).filter_by(batch_id=bid).all()
    return [
        {
            "id": e.id,
            "pred": e.pred,
            "conf": e.conf,
            "target": e.target,
            "image_ref": e.image_ref,
            "ts": str(e.ts),
        }
        for e in evts
    ]
