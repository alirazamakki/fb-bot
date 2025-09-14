from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email_or_phone = Column(String(255))
    encrypted_password = Column(String(2048), nullable=True)
    profile_path = Column(Text, nullable=False)
    proxy_id = Column(Integer, ForeignKey("proxies.id"), nullable=True)
    last_seen = Column(DateTime, nullable=True)
    status = Column(String(32), default="ok")
    notes = Column(Text, nullable=True)

    groups = relationship("Group", back_populates="account", cascade="all, delete-orphan")
    proxy = relationship("Proxy", back_populates="accounts")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    fb_group_id = Column(String(255))
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    name = Column(String(255))
    url = Column(Text)
    members = Column(Integer, default=0)
    posting_permission = Column(Boolean, default=True)
    excluded = Column(Boolean, default=False)
    last_posted_at = Column(DateTime, nullable=True)

    account = relationship("Account", back_populates="groups")


class Poster(Base):
    __tablename__ = "posters"

    id = Column(Integer, primary_key=True)
    filename = Column(String(512))
    filepath = Column(Text)
    category = Column(String(255), nullable=True)
    tags = Column(JSON, default=list)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    metadata = Column(JSON, default=dict)


class Caption(Base):
    __tablename__ = "captions"

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    category = Column(String(255), nullable=True)
    tags = Column(JSON, default=list)
    uniqueness_mode = Column(String(64), default="none")


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True)
    url = Column(Text)
    category = Column(String(255), nullable=True)
    weight = Column(Integer, default=1)


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    config_json = Column(JSON, default=dict)
    status = Column(String(32), default="draft")

    tasks = relationship("CampaignTask", back_populates="campaign", cascade="all, delete-orphan")


class CampaignTask(Base):
    __tablename__ = "campaign_tasks"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    poster_id = Column(Integer, ForeignKey("posters.id"), nullable=True)
    caption_id = Column(Integer, ForeignKey("captions.id"), nullable=True)
    link_id = Column(Integer, ForeignKey("links.id"), nullable=True)
    scheduled_time = Column(DateTime, nullable=True)
    status = Column(String(32), default="pending")
    retries_done = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)

    campaign = relationship("Campaign", back_populates="tasks")
    account = relationship("Account")
    group = relationship("Group")
    poster = relationship("Poster")
    caption = relationship("Caption")
    link = relationship("Link")


class Proxy(Base):
    __tablename__ = "proxies"

    id = Column(Integer, primary_key=True)
    host = Column(String(255))
    port = Column(Integer)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    type = Column(String(32), default="HTTP")

    accounts = relationship("Account", back_populates="proxy")


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    level = Column(String(16), default="INFO")
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    message = Column(Text)
    extra_json = Column(JSON, default=dict)

