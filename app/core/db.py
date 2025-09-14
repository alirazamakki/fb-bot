from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import AppConfig


class Base(DeclarativeBase):
	pass


_engine = None
_SessionLocal: sessionmaker[Session] | None = None


def initialize_database(config: AppConfig) -> None:
	global _engine, _SessionLocal
	if _engine is not None:
		return
	# SQLite URL
	db_url = f"sqlite:///{config.database_path}"
	_engine = create_engine(db_url, echo=False, future=True)
	_SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)
	# Import models to ensure table metadata is registered
	from app.core import models as _models  # noqa: F401
	Base.metadata.create_all(_engine)


@contextmanager

def db_session() -> Iterator[Session]:
	if _SessionLocal is None:
		raise RuntimeError("Database not initialized. Call initialize_database() first.")
	session = _SessionLocal()
	try:
		yield session
		session.commit()
	except Exception:
		session.rollback()
		raise
	finally:
		session.close()