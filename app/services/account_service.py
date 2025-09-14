from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, delete

from app.core.db import db_session
from app.core.models import Account, Group


def list_accounts() -> List[Account]:
	with db_session() as s:
		return list(s.scalars(select(Account).order_by(Account.id.desc())))


def create_account(name: str, profile_path: str, email_or_phone: Optional[str] = None) -> Account:
	with db_session() as s:
		acc = Account(name=name, profile_path=profile_path, email_or_phone=email_or_phone)
		s.add(acc)
		s.flush()
		return acc


def update_account(account_id: int, *, name: Optional[str] = None, profile_path: Optional[str] = None, email_or_phone: Optional[str] = None, status: Optional[str] = None) -> None:
	with db_session() as s:
		acc = s.get(Account, account_id)
		if not acc:
			raise ValueError("Account not found")
		if name is not None:
			acc.name = name
		if profile_path is not None:
			acc.profile_path = profile_path
		if email_or_phone is not None:
			acc.email_or_phone = email_or_phone
		if status is not None:
			acc.status = status


def delete_account(account_id: int) -> None:
	with db_session() as s:
		acc = s.get(Account, account_id)
		if not acc:
			return
		s.delete(acc)


def list_groups_for_account(account_id: int) -> List[Group]:
	with db_session() as s:
		return list(s.scalars(select(Group).where(Group.account_id == account_id).order_by(Group.id.desc())))


def stub_fetch_groups(account_id: int) -> int:
	"""Stub: create a couple of sample groups for the account if none exist."""
	with db_session() as s:
		acc = s.get(Account, account_id)
		if not acc:
			raise ValueError("Account not found")
		existing = s.scalars(select(Group).where(Group.account_id == account_id)).first()
		if existing:
			return 0
		g1 = Group(
			fb_group_id="sample-1",
			account_id=account_id,
			name="Sample Group One",
			url="https://www.facebook.com/groups/sample1",
			members=12345,
			posting_permission=True,
		)
		g2 = Group(
			fb_group_id="sample-2",
			account_id=account_id,
			name="Sample Group Two",
			url="https://www.facebook.com/groups/sample2",
			members=6789,
			posting_permission=True,
		)
		s.add_all([g1, g2])
		return 2