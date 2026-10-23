"""Idempotent retry: same portion id twice -> single event."""

import os

for f in [
    "./data/test_idem.sqlite3",
    "./data/test_idem.sqlite3-wal",
    "./data/test_idem.sqlite3-shm",
]:
    try:
        os.remove(f)
    except FileNotFoundError:
        pass
from sqlalchemy import create_engine
from sqlalchemy import event as _event

import app.db as _db

_db.engine.dispose()
_db.engine = create_engine(
    "sqlite:///./data/test_idem.sqlite3", connect_args={"check_same_thread": False}
)


@_event.listens_for(_db.engine, "connect")
def _wal(dbapi_conn, _rec):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.close()


import sqlalchemy.orm as _orm

_db.SessionLocal = _orm.sessionmaker(bind=_db.engine, autoflush=False, autocommit=False)
from app.db import init_db

init_db()
from fastapi.testclient import TestClient

import app.main as _main

client = TestClient(_main.app)
from app import models


def test_idempotent_portion():
    s = _db.SessionLocal()
    s.add(models.Producer(id="prod-T", display_name="T", locality="x", contact_private="x"))
    s.commit()
    s.close()
    b = client.post(
        "/api/batches",
        json={
            "producer_id": "prod-T",
            "harvest_date": "2026-10-20",
            "locality": "x",
            "grade": "premium",
            "unit_ask": 10,
        },
    ).json()
    p1 = client.post(
        f"/api/batches/{b['id']}/portions?mode=B",
        json={"id": "evt-dup-1", "pred": "accepted", "conf": 0.9},
    ).json()
    p2 = client.post(
        f"/api/batches/{b['id']}/portions?mode=B",
        json={"id": "evt-dup-1", "pred": "accepted", "conf": 0.9},
    ).json()
    assert p2.get("idempotent") is True
    s = _db.SessionLocal()
    n = s.query(models.PortionEvent).filter_by(id="evt-dup-1").count()
    s.close()
    assert n == 1
