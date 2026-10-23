"""HER-GRADE FastAPI entry — single self-hosted image, offline demo."""

import os

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import models
from .db import get_db, init_db
from .routers import batches, orders, pricing, public, requests, station

init_db()
app = FastAPI(title="HER-GRADE Phase 1")
for r, prefix in [
    (public, ""),
    (batches, "/api/batches"),
    (requests, "/api/requests"),
    (orders, "/api/orders"),
    (pricing, "/api/pricing"),
    (station, "/api/station"),
]:
    app.include_router(r.router, prefix=prefix)

os.makedirs("app/static", exist_ok=True)
os.makedirs("app/templates", exist_ok=True)
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except Exception:
    pass
templates = Jinja2Templates(directory="app/templates")


@app.get("/health")
def health():
    return {
        "ok": True,
        "track": "Track 2",
        "mode": "phase1-local",
        "herb_locked": "rosemary",
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    nb = db.query(models.Batch).count()
    nr = db.query(models.BuyerRequest).count()
    no = db.query(models.CollectiveOrder).count()
    return templates.TemplateResponse(request, "index.html", {"nb": nb, "nr": nr, "no": no})


@app.get("/producer", response_class=HTMLResponse)
def producer_page(request: Request, db: Session = Depends(get_db)):
    prods = db.query(models.Producer).all()
    batches = db.query(models.Batch).order_by(models.Batch.created_at.desc()).limit(20).all()
    return templates.TemplateResponse(
        request, "producer.html", {"prods": prods, "batches": batches}
    )


@app.get("/station", response_class=HTMLResponse)
def station_page(request: Request):
    return templates.TemplateResponse(request, "station.html", {})


@app.get("/buyer", response_class=HTMLResponse)
def buyer_page(request: Request, db: Session = Depends(get_db)):
    reqs = (
        db.query(models.BuyerRequest)
        .order_by(models.BuyerRequest.created_at.desc())
        .limit(20)
        .all()
    )
    orders = (
        db.query(models.CollectiveOrder)
        .order_by(models.CollectiveOrder.created_at.desc())
        .limit(20)
        .all()
    )
    return templates.TemplateResponse(request, "buyer.html", {"reqs": reqs, "orders": orders})


@app.get("/batch/{bid}", response_class=HTMLResponse)
def batch_page(bid: str, request: Request, db: Session = Depends(get_db)):
    b = db.get(models.Batch, bid)
    evts = db.query(models.PortionEvent).filter_by(batch_id=bid).all() if b else []
    return templates.TemplateResponse(request, "batch.html", {"b": b, "evts": evts})
