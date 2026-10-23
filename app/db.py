"""HER-GRADE DB — SQLite WAL, zero-ops local."""

import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

os.makedirs(
    (
        os.path.dirname(os.path.abspath(settings.db_path))
        if os.path.dirname(settings.db_path) not in ("", ".")
        else "."
    ),
    exist_ok=True,
)
# ensure data dir exists for relative path
os.makedirs("./data", exist_ok=True)
os.makedirs("./data/batches", exist_ok=True)

engine = create_engine(f"sqlite:///{settings.db_path}", connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def _wal(dbapi_conn, _rec):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("PRAGMA synchronous=NORMAL;")
    cur.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from . import models  # noqa: F401 — register tables

    Base.metadata.create_all(bind=engine)
