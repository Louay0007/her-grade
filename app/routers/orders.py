"""Collective orders: proposal -> per-producer + buyer confirm -> confirmed."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db

router = APIRouter()


@router.post("")
def create_order(body: schemas.OrderCreate, db: Session = Depends(get_db)):
    r = db.get(models.BuyerRequest, body.request_id)
    if not r:
        raise HTTPException(404, "request not found")
    o = models.CollectiveOrder(
        request_id=r.id,
        status="proposed",
        total_g=sum(c["qty_g"] for c in body.contributions),
    )
    db.add(o)
    db.flush()
    for c in body.contributions:
        b = db.get(models.Batch, c["batch_id"])
        if not b:
            raise HTTPException(404, f"batch {c['batch_id']} not found")
        if c["qty_g"] > b.avail_g:
            raise HTTPException(409, f"batch {b.id} only has {b.avail_g}g available")
        db.add(
            models.OrderContribution(
                order_id=o.id,
                batch_id=b.id,
                producer_id=b.producer_id,
                qty_g=c["qty_g"],
                unit_price=b.unit_ask or 0,
                grade=b.grade,
            )
        )
    db.commit()
    db.refresh(o)
    lines = db.query(models.OrderContribution).filter_by(order_id=o.id).all()
    return {
        "id": o.id,
        "status": o.status,
        "total_g": o.total_g,
        "lines": [
            {
                "batch_id": l.batch_id,
                "producer_id": l.producer_id,
                "qty_g": l.qty_g,
                "unit_price": l.unit_price,
                "grade": l.grade,
            }
            for l in lines
        ],
    }


@router.get("/{oid}")
def get_order(oid: str, db: Session = Depends(get_db)):
    o = db.get(models.CollectiveOrder, oid)
    if not o:
        raise HTTPException(404, "order not found")
    lines = db.query(models.OrderContribution).filter_by(order_id=oid).all()
    return {
        "id": o.id,
        "request_id": o.request_id,
        "status": o.status,
        "total_g": o.total_g,
        "lines": [
            {
                "batch_id": l.batch_id,
                "producer_id": l.producer_id,
                "qty_g": l.qty_g,
                "unit_price": l.unit_price,
                "grade": l.grade,
                "producer_confirmed": l.producer_confirmed,
                "buyer_confirmed": l.buyer_confirmed,
            }
            for l in lines
        ],
    }


@router.post("/{oid}/confirm")
def confirm_order(oid: str, body: schemas.ConfirmIn, db: Session = Depends(get_db)):
    o = db.get(models.CollectiveOrder, oid)
    if not o:
        raise HTTPException(404, "order not found")
    lines = db.query(models.OrderContribution).filter_by(order_id=oid).all()
    if body.role.startswith("producer"):
        if not body.producer_id:
            raise HTTPException(422, "producer_id required")
        mine = [l for l in lines if l.producer_id == body.producer_id]
        if not mine:
            raise HTTPException(404, "no contribution for this producer")
        for l in mine:
            l.producer_confirmed = True
    elif body.role == "buyer":
        for l in lines:
            l.buyer_confirmed = True
    else:
        raise HTTPException(422, "role must be producer:<id> or buyer")
    all_p = all(l.producer_confirmed for l in lines)
    all_b = all(l.buyer_confirmed for l in lines)
    if all_p and all_b:
        o.status = "confirmed"
        # decrement availability once, preserve separate batch IDs
        for l in lines:
            b = db.get(models.Batch, l.batch_id)
            b.avail_g = max(0, (b.avail_g or 0) - l.qty_g)
            if b.avail_g == 0:
                b.status = "committed"
    db.commit()
    return {
        "id": o.id,
        "status": o.status,
        "all_producers_confirmed": all_p,
        "buyer_confirmed": all_b,
    }
