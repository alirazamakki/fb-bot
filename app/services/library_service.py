from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from sqlalchemy import select

from app.core.config import AppConfig
from app.core.db import db_session
from app.core.models import Poster, Caption, Link


def add_poster(filepath: str, category: Optional[str] = None, tags_json: Optional[str] = None) -> Poster:
	p = Path(filepath)
	if not p.exists():
		raise FileNotFoundError(filepath)
	with db_session() as s:
		poster = Poster(
			filename=p.name,
			filepath=str(p.resolve()),
			category=category,
			tags=json.loads(tags_json) if tags_json else None,
		)
		s.add(poster)
		s.flush()
		return poster


def list_posters() -> List[Poster]:
	with db_session() as s:
		return list(s.scalars(select(Poster).order_by(Poster.id.desc())))


def delete_poster(poster_id: int) -> None:
	with db_session() as s:
		obj = s.get(Poster, poster_id)
		if obj:
			s.delete(obj)


def add_caption(text: str, category: Optional[str] = None, tags_json: Optional[str] = None, uniqueness_mode: Optional[str] = None) -> Caption:
	with db_session() as s:
		cap = Caption(
			text=text,
			category=category,
			tags=json.loads(tags_json) if tags_json else None,
			uniqueness_mode=uniqueness_mode,
		)
		s.add(cap)
		s.flush()
		return cap


def list_captions() -> List[Caption]:
	with db_session() as s:
		return list(s.scalars(select(Caption).order_by(Caption.id.desc())))


def delete_caption(caption_id: int) -> None:
	with db_session() as s:
		obj = s.get(Caption, caption_id)
		if obj:
			s.delete(obj)


def add_link(url: str, category: Optional[str] = None, weight: int = 1) -> Link:
	with db_session() as s:
		link = Link(url=url, category=category, weight=weight)
		s.add(link)
		s.flush()
		return link


def list_links() -> List[Link]:
	with db_session() as s:
		return list(s.scalars(select(Link).order_by(Link.id.desc())))


def delete_link(link_id: int) -> None:
	with db_session() as s:
		obj = s.get(Link, link_id)
		if obj:
			s.delete(obj)