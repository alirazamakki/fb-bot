from __future__ import annotations

from sqlalchemy import Engine

from fb_marketer.db.models import Base


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(engine)

