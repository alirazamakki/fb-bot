from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Account(Base):
	__tablename__ = "accounts"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(200), nullable=False)
	email_or_phone: Mapped[Optional[str]] = mapped_column(String(200))
	encrypted_password: Mapped[Optional[str]] = mapped_column(String(500))
	profile_path: Mapped[str] = mapped_column(String(1000), nullable=False)
	proxy_id: Mapped[Optional[int]] = mapped_column(ForeignKey("proxies.id"))
	last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False))
	status: Mapped[str] = mapped_column(String(50), default="ok")
	notes: Mapped[Optional[str]] = mapped_column(Text)

	groups: Mapped[List[Group]] = relationship(back_populates="account", cascade="all, delete-orphan")  # type: ignore[name-defined]
	campaign_tasks: Mapped[List[CampaignTask]] = relationship(back_populates="account")  # type: ignore[name-defined]


class Group(Base):
	__tablename__ = "groups"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	fb_group_id: Mapped[str] = mapped_column(String(200), index=True)
	account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
	name: Mapped[Optional[str]] = mapped_column(String(500))
	url: Mapped[Optional[str]] = mapped_column(String(1000))
	members: Mapped[Optional[int]] = mapped_column(Integer)
	posting_permission: Mapped[bool] = mapped_column(Boolean, default=True)
	excluded: Mapped[bool] = mapped_column(Boolean, default=False)
	last_posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False))

	account: Mapped[Account] = relationship(back_populates="groups")  # type: ignore[name-defined]
	campaign_tasks: Mapped[List[CampaignTask]] = relationship(back_populates="group")  # type: ignore[name-defined]


class Poster(Base):
	__tablename__ = "posters"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	filename: Mapped[str] = mapped_column(String(500))
	filepath: Mapped[str] = mapped_column(String(1000))
	category: Mapped[Optional[str]] = mapped_column(String(200))
	tags: Mapped[Optional[dict]] = mapped_column(JSON)
	width: Mapped[Optional[int]] = mapped_column(Integer)
	height: Mapped[Optional[int]] = mapped_column(Integer)
	image_metadata: Mapped[Optional[dict]] = mapped_column(JSON)

	campaign_tasks: Mapped[List[CampaignTask]] = relationship(back_populates="poster")  # type: ignore[name-defined]


class Caption(Base):
	__tablename__ = "captions"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	text: Mapped[str] = mapped_column(Text)
	category: Mapped[Optional[str]] = mapped_column(String(200))
	tags: Mapped[Optional[dict]] = mapped_column(JSON)
	uniqueness_mode: Mapped[Optional[str]] = mapped_column(String(50))

	campaign_tasks: Mapped[List[CampaignTask]] = relationship(back_populates="caption")  # type: ignore[name-defined]


class Link(Base):
	__tablename__ = "links"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	url: Mapped[str] = mapped_column(String(1000), nullable=False)
	category: Mapped[Optional[str]] = mapped_column(String(200))
	weight: Mapped[int] = mapped_column(Integer, default=1)

	campaign_tasks: Mapped[List[CampaignTask]] = relationship(back_populates="link")  # type: ignore[name-defined]


class Campaign(Base):
	__tablename__ = "campaigns"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(300), nullable=False)
	config_json: Mapped[Optional[dict]] = mapped_column(JSON)
	status: Mapped[str] = mapped_column(String(50), default="pending")
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, onupdate=datetime.utcnow)

	tasks: Mapped[List[CampaignTask]] = relationship(back_populates="campaign", cascade="all, delete-orphan")  # type: ignore[name-defined]


class CampaignTask(Base):
	__tablename__ = "campaign_tasks"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), index=True)
	account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
	group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), index=True)
	poster_id: Mapped[Optional[int]] = mapped_column(ForeignKey("posters.id"))
	caption_id: Mapped[Optional[int]] = mapped_column(ForeignKey("captions.id"))
	link_id: Mapped[Optional[int]] = mapped_column(ForeignKey("links.id"))
	scheduled_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False))
	status: Mapped[str] = mapped_column(String(50), default="pending")
	retries_done: Mapped[int] = mapped_column(Integer, default=0)
	last_error: Mapped[Optional[str]] = mapped_column(Text)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, onupdate=datetime.utcnow)

	campaign: Mapped[Campaign] = relationship(back_populates="tasks")  # type: ignore[name-defined]
	account: Mapped[Account] = relationship(back_populates="campaign_tasks")  # type: ignore[name-defined]
	group: Mapped[Group] = relationship(back_populates="campaign_tasks")  # type: ignore[name-defined]
	poster: Mapped[Optional[Poster]] = relationship(back_populates="campaign_tasks")  # type: ignore[name-defined]
	caption: Mapped[Optional[Caption]] = relationship(back_populates="campaign_tasks")  # type: ignore[name-defined]
	link: Mapped[Optional[Link]] = relationship(back_populates="campaign_tasks")  # type: ignore[name-defined]


class Proxy(Base):
	__tablename__ = "proxies"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	host: Mapped[str] = mapped_column(String(300), nullable=False)
	port: Mapped[int] = mapped_column(Integer, nullable=False)
	username: Mapped[Optional[str]] = mapped_column(String(200))
	password: Mapped[Optional[str]] = mapped_column(String(200))
	type: Mapped[str] = mapped_column(String(50), default="HTTP")

	accounts: Mapped[List[Account]] = relationship(backref="proxy")  # type: ignore[name-defined]


class LogEntry(Base):
	__tablename__ = "logs"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, index=True)
	level: Mapped[str] = mapped_column(String(20), default="INFO")
	account_id: Mapped[Optional[int]] = mapped_column(ForeignKey("accounts.id"), index=True)
	group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("groups.id"), index=True)
	message: Mapped[str] = mapped_column(Text)
	extra_json: Mapped[Optional[dict]] = mapped_column(JSON)