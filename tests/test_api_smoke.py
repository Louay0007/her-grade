"""API smoke: seed -> batch flow -> request -> matches -> order -> confirm -> price -> QR page."""

import os

os.environ["DB_PATH"] = "./data/test_smoke.sqlite3"

for f in [
    "./data/test_smoke.sqlite3",
    "./data/test_smoke.sqlite3-wal",
    "./data/test_smoke.sqlite3-shm",
]:
    try:
        os.remove(f)
    except FileNotFoundError:
        pass

from fastapi.testclient import TestClient

from app import db as _db

_db.engine.dispose()
# re-point engine to test db
from sqlalchemy import create_engine
from sqlalchemy import event as _event

_db.engine = create_engine(
    "sqlite:///./data/test_smoke.sqlite3", connect_args={"check_same_thread": False}
)


@_event.listens_for(_db.engine, "connect")
def _wal(dbapi_conn, _rec):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.close()


from app.db import SessionLocal as _SL

_db.SessionLocal = _SL = __import__("sqlalchemy.orm", fromlist=["sessionmaker"]).sessionmaker(
    bind=_db.engine, autoflush=False, autocommit=False
)
import app.main as _main
from app.db import init_db

init_db()
client = TestClient(_main.app)


def test_full_demo_flow():
    # seed producers directly
    from app import models

    s = _db.SessionLocal()
    s.add(
        models.Producer(
            id="prod-A",
            display_name="Producer A (TEST)",
            locality="Sejnane (level)",
            contact_private="x",
        )
    )
    s.add(
        models.Producer(
            id="prod-B",
            display_name="Producer B (TEST)",
            locality="Sejnane (level)",
            contact_private="x",
        )
    )
    s.commit()
    s.close()

    b1 = client.post(
        "/api/batches",
        json={
            "producer_id": "prod-A",
            "herb_type": "rosemary",
            "harvest_date": "2026-10-20",
            "locality": "Sejnane (level)",
            "grade": "premium",
            "unit_ask": 12,
        },
    ).json()
    b2 = client.post(
        "/api/batches",
        json={
            "producer_id": "prod-B",
            "herb_type": "rosemary",
            "harvest_date": "2026-10-21",
            "locality": "Sejnane (level)",
            "grade": "premium",
            "unit_ask": 12,
        },
    ).json()
    assert b1["herb_type"] == "rosemary" and b2["herb_type"] == "rosemary"

    # feed portions: A gets 550x20g=11kg accepted, B gets 450x20g=9kg
    for _ in range(5):
        r = client.post(
            f"/api/batches/{b1['id']}/portions?mode=B",
            json={"pred": "accepted", "conf": 0.9, "image_ref": "img.jpg"},
        )
        assert r.status_code == 200, r.text
    # idempotency check
    eid = "evt-fixed-001"
    r1 = client.post(
        f"/api/batches/{b1['id']}/portions?mode=B",
        json={"id": eid, "pred": "accepted", "conf": 0.9},
    )
    r2 = client.post(
        f"/api/batches/{b1['id']}/portions?mode=B",
        json={"id": eid, "pred": "accepted", "conf": 0.9},
    )
    assert r2.json().get("idempotent") is True

    # Mode A uncertain -> stop_alert path still logs portion
    ra = client.post(
        f"/api/batches/{b1['id']}/portions?mode=A",
        json={"pred": "accepted", "conf": 0.4},
    )
    assert ra.json()["action"] == "stop_alert"

    f1 = client.post(f"/api/batches/{b1['id']}/finish").json()
    f2 = client.post(f"/api/batches/{b2['id']}/finish").json()
    assert f1["status"] == "published" and "qr_url" in f1

    # bump avail to demo 11+9kg without feeding 1000 portions
    s = _db.SessionLocal()
    ba = s.get(models.Batch, b1["id"])
    bb = s.get(models.Batch, b2["id"])
    ba.accepted_g = 11000
    ba.total_g = 11200
    ba.verify_g = 200
    ba.avail_g = 11000
    bb.accepted_g = 9000
    bb.total_g = 9000
    bb.verify_g = 0
    bb.avail_g = 9000
    s.commit()
    s.close()

    rq = client.post(
        "/api/requests",
        json={
            "herb_type": "rosemary",
            "qty_need_g": 20000,
            "grade_required": "premium",
            "harvest_from": "2026-10-15",
            "harvest_to": "2026-10-25",
            "max_price": 14,
            "delivery_place": "Tunis",
            "deadline": "2026-11-05",
        },
    ).json()
    mt = client.get(f"/api/requests/{rq['id']}/matches").json()
    assert mt["total_g"] == 20000 and not mt["partial"], mt

    od = client.post(
        "/api/orders",
        json={
            "request_id": rq["id"],
            "contributions": [
                {"batch_id": b1["id"], "qty_g": 11000},
                {"batch_id": b2["id"], "qty_g": 9000},
            ],
        },
    ).json()
    assert od["total_g"] == 20000
    c1 = client.post(
        f"/api/orders/{od['id']}/confirm",
        json={"role": "producer:x", "producer_id": "prod-A"},
    ).json()
    assert c1["status"] == "proposed"
    c2 = client.post(
        f"/api/orders/{od['id']}/confirm",
        json={"role": "producer:x", "producer_id": "prod-B"},
    ).json()
    cb = client.post(f"/api/orders/{od['id']}/confirm", json={"role": "buyer"}).json()
    assert cb["status"] == "confirmed", cb

    pr = client.post(
        "/api/pricing/calc",
        json={
            "cprod": 8,
            "cproc": 0,
            "cpack": 1,
            "ctrans": 0.5,
            "cfees": 0.5,
            "psale": 12,
            "qty_kg": 20,
        },
    ).json()
    assert pr["ctotal"] == 10.0 and pr["mkg"] == 2.0

    pub = client.get(f"/b/{b1['id']}")
    assert pub.status_code == 200 and "rosemary" in pub.text.lower()
    assert "contact" not in pub.text.lower() or "contacts" not in pub.text.lower()

    h = client.get("/health").json()
    assert h["ok"] and h["herb_locked"] == "rosemary"
