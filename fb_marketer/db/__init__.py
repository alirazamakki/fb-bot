from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fb_marketer.config import load_config


def get_engine():
    cfg = load_config()
    engine = create_engine(cfg.db_url, future=True, echo=False)
    return engine


SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)

