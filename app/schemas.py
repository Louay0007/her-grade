"""HER-GRADE pydantic schemas."""

from pydantic import BaseModel, Field


class BatchCreate(BaseModel):
    producer_id: str
    herb_type: str = Field(default="rosemary", pattern="^(rosemary)$")  # P1 LOCKED
    harvest_date: str  # YYYY-MM-DD as entered
    locality: str = ""
    grade: str = "premium"
    avail_g: int = 0
    unit_ask: float = 0.0


class PortionIn(BaseModel):
    id: str | None = None  # uuid for idempotency; generated if missing
    image_ref: str = ""
    pred: str = "verify"  # accepted | verify (from vision)
    conf: float = 0.0
    area_ok: bool = True
    overlap: bool = False


class RequestCreate(BaseModel):
    herb_type: str = "rosemary"
    qty_need_g: int
    grade_required: str = "premium"
    harvest_from: str = ""
    harvest_to: str = ""
    max_price: float = 9999.0
    delivery_place: str = ""
    deadline: str = ""
    needs_qr: bool = True


class OrderCreate(BaseModel):
    request_id: str
    contributions: list[dict]  # [{batch_id, qty_g}]


class ConfirmIn(BaseModel):
    role: str  # producer:<producer_id> | buyer
    producer_id: str | None = None


class PricingIn(BaseModel):
    cprod: float = 0
    cproc: float = 0
    cpack: float = 0
    ctrans: float = 0
    cfees: float = 0
    psale: float = 0
    qty_kg: float = 0


class ModeIn(BaseModel):
    mode: str  # A | B
