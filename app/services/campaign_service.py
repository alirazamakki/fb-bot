from __future__ import annotations

from typing import Iterable, List, Optional

from sqlalchemy import select

from app.core.db import db_session
from app.core.models import Campaign, CampaignTask, Account, Group


def create_campaign(name: str, config: dict, account_ids: Iterable[int]) -> Campaign:
	with db_session() as s:
		campaign = Campaign(name=name, config_json=config, status="pending")
		s.add(campaign)
		s.flush()
		# Build tasks: all groups for selected accounts
		for acc_id in account_ids:
			groups = s.scalars(select(Group).where(Group.account_id == acc_id, Group.excluded == False))  # noqa: E712
			for grp in groups:
				task = CampaignTask(
					campaign_id=campaign.id,
					account_id=acc_id,
					group_id=grp.id,
					status="pending",
				)
				s.add(task)
		return campaign


def list_campaigns() -> List[Campaign]:
	with db_session() as s:
		return list(s.scalars(select(Campaign).order_by(Campaign.id.desc())))


def list_campaign_tasks(campaign_id: int) -> List[CampaignTask]:
	with db_session() as s:
		return list(s.scalars(select(CampaignTask).where(CampaignTask.campaign_id == campaign_id).order_by(CampaignTask.id)))