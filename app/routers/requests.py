"""Buyer requests + matches (hard filter then rank, never merge grades silently)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..services import matching as m

router = APIRouter()


@router.post("")
def create_request(body: schemas.RequestCreate, db: Session = Depends(get_db)):
    r = models.BuyerRequest(
        herb_type="rosemary",
        qty_need_g=body.qty_need_g,
        grade_required=body.grade_required,
        harvest_from=body.harvest_from,
        harvest_to=body.harvest_to,
        max_price=body.max_price,
        delivery_place=body.delivery_place,
        deadline=body.deadline,
        needs_qr=body.needs_qr,
        status="open",
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return {
        "id": r.id,
        "herb_type": r.herb_type,
        "qty_need_g": r.qty_need_g,
        "status": r.status,
    }


@router.get("")
def list_requests(db: Session = Depends(get_db)):
    return [
        {
            "id": r.id,
            "herb_type": r.herb_type,
            "qty_need_g": r.qty_need_g,
            "grade_required": r.grade_required,
            "status": r.status,
        }
        for r in db.query(models.BuyerRequest).all()
    ]


@router.get("/{rid}/matches")
def get_matches(rid: str, db: Session = Depends(get_db)):
    r = db.get(models.BuyerRequest, rid)
    if not r:
        raise HTTPException(404, "request not found")
    req = {
        "herb_type": r.herb_type,
        "qty_need_g": r.qty_need_g,
        "grade_required": r.grade_required,
        "harvest_from": r.harvest_from or "",
        "harvest_to": r.harvest_to or "",
        "max_price": r.max_price,
        "needs_qr": r.needs_qr,
    }
    lots = []
    for b in db.query(models.Batch).filter(models.Batch.status.in_(["published", "ready"])).all():
        if b.avail_g <= 0:
            continue
        lots.append(
            {
                "id": f"lot-{b.id}",
                "batch_id": b.id,
                "producer_id": b.producer_id,
                "herb_type": b.herb_type,
                "grade": b.grade,
                "avail_g": b.avail_g,
                "harvest_date": b.harvest_date,
                "qr_id": b.qr_id or b.id,
                "status": "published",
                "unit_ask": b.unit_ask or 0,
                "visual_sim": 0.85,
                "delivery_band": "region",
            }
        )
    out = m.propose(req, lots)
    return {
        "request_id": rid,
        **out,
        "disclaimer": "Visual similarity experimental only; photo similarity != food safety.",
    }
