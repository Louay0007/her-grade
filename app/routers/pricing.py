"""Pricing calculator — support tool, illustrative until field validation."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..services import pricing as p

router = APIRouter()


@router.post("/calc")
def calc(body: schemas.PricingIn, db: Session = Depends(get_db)):
    costs = {
        "cprod": body.cprod,
        "cproc": body.cproc,
        "cpack": body.cpack,
        "ctrans": body.ctrans,
        "cfees": body.cfees,
    }
    out = p.calc(costs, body.psale, body.qty_kg)
    db.add(
        models.PriceLog(
            cprod=body.cprod,
            cproc=body.cproc,
            cpack=body.cpack,
            ctrans=body.ctrans,
            cfees=body.cfees,
            psale=body.psale,
            qty_kg=body.qty_kg,
            ctotal=out["ctotal"],
            mkg=out["mkg"],
            mtotal=out["mtotal"],
            below_cost=out["below_cost"],
        )
    )
    db.commit()
    return out
