"""HER-GRADE tables: Producer/Batch/PortionEvent/BuyerRequest/CollectiveOrder/OrderContribution/PriceLog."""

import datetime
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)

from .db import Base


def _uid(prefix=""):
    return f"{prefix}{uuid.uuid4().hex[:12]}"


class Producer(Base):
    __tablename__ = "producers"
    id = Column(String, primary_key=True, default=lambda: _uid("prod-"))
    display_name = Column(String, nullable=False)
    locality = Column(String, default="")
    contact_private = Column(String, default="")  # never exposed on /b/
    consent = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Batch(Base):
    __tablename__ = "batches"
    id = Column(String, primary_key=True, default=lambda: _uid("batch-"))
    producer_id = Column(String, ForeignKey("producers.id"), nullable=False)
    herb_type = Column(String, default="rosemary", nullable=False)  # P1 LOCKED: rosemary only
    harvest_date = Column(String, nullable=False)  # YYYY-MM-DD as entered
    locality = Column(String, default="")
    grade = Column(String, default="premium")  # premium | standard ; never merged silently
    total_g = Column(Integer, default=0)
    accepted_g = Column(Integer, default=0)
    verify_g = Column(Integer, default=0)
    avail_g = Column(Integer, default=0)
    unit_ask = Column(Float, default=0.0)  # DT/kg ask
    status = Column(String, default="open")  # open|published|ready|committed|finished
    qr_id = Column(String, default="")
    thresh_version = Column(String, default="v0.1-0.75")
    mode = Column(String, default="B")  # station mode at finish
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class PortionEvent(Base):
    __tablename__ = "portion_events"
    id = Column(String, primary_key=True, default=lambda: _uid("evt-"))
    batch_id = Column(String, ForeignKey("batches.id"), nullable=False)
    image_ref = Column(String, default="")
    pred = Column(String, default="verify")  # accepted | verify
    conf = Column(Float, default=0.0)
    target = Column(String, default="verify")  # accepted | verify box
    thresh_version = Column(String, default="v0.1-0.75")
    ts = Column(DateTime, default=datetime.datetime.utcnow)


class BuyerRequest(Base):
    __tablename__ = "buyer_requests"
    id = Column(String, primary_key=True, default=lambda: _uid("req-"))
    herb_type = Column(String, default="rosemary", nullable=False)
    qty_need_g = Column(Integer, nullable=False)
    grade_required = Column(String, default="premium")
    harvest_from = Column(String, default="")  # YYYY-MM-DD or ""
    harvest_to = Column(String, default="")
    max_price = Column(Float, default=9999.0)  # DT/kg
    delivery_place = Column(String, default="")
    deadline = Column(String, default="")
    needs_qr = Column(Boolean, default=True)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class CollectiveOrder(Base):
    __tablename__ = "collective_orders"
    id = Column(String, primary_key=True, default=lambda: _uid("ord-"))
    request_id = Column(String, ForeignKey("buyer_requests.id"), nullable=False)
    status = Column(String, default="proposed")  # proposed|confirmed|declined|partial
    total_g = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class OrderContribution(Base):
    __tablename__ = "order_contributions"
    id = Column(String, primary_key=True, default=lambda: _uid("contrib-"))
    order_id = Column(String, ForeignKey("collective_orders.id"), nullable=False)
    batch_id = Column(String, ForeignKey("batches.id"), nullable=False)
    producer_id = Column(String, ForeignKey("producers.id"), nullable=False)
    qty_g = Column(Integer, nullable=False)
    unit_price = Column(Float, default=0.0)
    grade = Column(String, default="premium")
    producer_confirmed = Column(Boolean, default=False)
    buyer_confirmed = Column(Boolean, default=False)


class PriceLog(Base):
    __tablename__ = "price_logs"
    id = Column(String, primary_key=True, default=lambda: _uid("price-"))
    cprod = Column(Float, default=0)
    cproc = Column(Float, default=0)
    cpack = Column(Float, default=0)
    ctrans = Column(Float, default=0)
    cfees = Column(Float, default=0)
    psale = Column(Float, default=0)
    qty_kg = Column(Float, default=0)
    ctotal = Column(Float, default=0)
    mkg = Column(Float, default=0)
    mtotal = Column(Float, default=0)
    below_cost = Column(Boolean, default=False)
    ts = Column(DateTime, default=datetime.datetime.utcnow)
