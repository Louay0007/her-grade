"""Seed TEST marketplace: producerA 11kg + producerB 9kg rosemary, buyer 20kg. Run: make seed."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import models
from app.db import SessionLocal, init_db

init_db()
db = SessionLocal()
# wipe TEST data
for m in [
    models.OrderContribution,
    models.CollectiveOrder,
    models.BuyerRequest,
    models.PortionEvent,
    models.Batch,
    models.Producer,
]:
    db.query(m).delete()
db.commit()

pa = models.Producer(
    id="prod-A",
    display_name="Producer A (TEST)",
    locality="Sejnane (level)",
    contact_private="TEST ONLY",
)
pb = models.Producer(
    id="prod-B",
    display_name="Producer B (TEST)",
    locality="Sejnane (level)",
    contact_private="TEST ONLY",
)
db.add_all([pa, pb])
db.commit()

ba = models.Batch(
    id="batch-A11",
    producer_id="prod-A",
    herb_type="rosemary",
    harvest_date="2026-10-20",
    locality="Sejnane (level)",
    grade="premium",
    total_g=11000,
    accepted_g=11000,
    verify_g=0,
    avail_g=11000,
    unit_ask=12.0,
    status="published",
    qr_id="batch-A11",
    thresh_version="v0.1-0.75",
    mode="B",
)
bb = models.Batch(
    id="batch-B09",
    producer_id="prod-B",
    herb_type="rosemary",
    harvest_date="2026-10-21",
    locality="Sejnane (level)",
    grade="premium",
    total_g=9000,
    accepted_g=9000,
    verify_g=0,
    avail_g=9000,
    unit_ask=12.0,
    status="published",
    qr_id="batch-B09",
    thresh_version="v0.1-0.75",
    mode="B",
)
db.add_all([ba, bb])
db.commit()

rq = models.BuyerRequest(
    id="req-20kg",
    herb_type="rosemary",
    qty_need_g=20000,
    grade_required="premium",
    harvest_from="2026-10-15",
    harvest_to="2026-10-25",
    max_price=14.0,
    delivery_place="Tunis",
    deadline="2026-11-05",
    needs_qr=True,
    status="open",
)
db.add(rq)
db.commit()
print("seeded: prod-A/prod-B, batch-A11 (11kg) + batch-B09 (9kg) rosemary premium, req-20kg (20kg)")
print("accounts (TEST): producer1/test producer2/test buyer1/test — map to prod-A/prod-B in demo")
