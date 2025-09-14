from __future__ import annotations

import random
import time
from typing import Callable, Iterable, List, Optional

from sqlalchemy import select

from app.core.queue_manager import PoolManager, WorkerTask
from app.core.db import db_session
from app.core.models import Campaign, CampaignTask, Account, Group, Poster, Caption, Link
from app.core.playwright_controller import PlaywrightController

ProgressCallback = Callable[[str, dict], None]


class WorkerService:
	"""Service to run a campaign's tasks with fixed concurrency and progress callbacks."""

	def __init__(self, on_progress: Optional[ProgressCallback] = None) -> None:
		self._on_progress = on_progress or (lambda event, payload: None)
		self._pool: PoolManager | None = None
		self._cancelled = False

	def cancel(self) -> None:
		self._cancelled = True
		if self._pool:
			self._pool.stop()

	def run_campaign(self, campaign_id: int, batch_size: int) -> None:
		# Load pending tasks grouped by account
		with db_session() as s:
			campaign = s.get(Campaign, campaign_id)
			if not campaign:
				raise ValueError("Campaign not found")
			tasks = list(s.scalars(select(CampaignTask).where(CampaignTask.campaign_id == campaign_id, CampaignTask.status == "pending")))
			account_ids = sorted({t.account_id for t in tasks})

		self._pool = PoolManager(batch_size=batch_size)
		self._pool.submit_tasks(WorkerTask(account_id=acc_id, payload={"campaign_id": campaign_id}) for acc_id in account_ids)
		self._pool.run(lambda t: self._run_account(campaign_id, t.account_id))

	def _emit(self, event: str, **payload: object) -> None:
		self._on_progress(event, payload)  # type: ignore[arg-type]

	def _run_account(self, campaign_id: int, account_id: int) -> None:
		if self._cancelled:
			return
		with db_session() as s:
			campaign = s.get(Campaign, campaign_id)
			account = s.get(Account, account_id)
			if not account or not campaign:
				return
			config = campaign.config_json or {}
			poster_ids = config.get("poster_ids") or []
			caption_ids = config.get("caption_ids") or []
			link_ids = config.get("link_ids") or []
			delay_min = int(config.get("delay_min", 5))
			delay_max = int(config.get("delay_max", 10))

			# Prefetch assets into memory for random selection
			posters = list(s.scalars(select(Poster).where(Poster.id.in_(poster_ids)))) if poster_ids else []
			captions = list(s.scalars(select(Caption).where(Caption.id.in_(caption_ids)))) if caption_ids else []
			links = list(s.scalars(select(Link).where(Link.id.in_(link_ids)))) if link_ids else []

			self._emit("account_start", campaign_id=campaign_id, account_id=account_id, account_name=account.name)

			pending = list(s.scalars(select(CampaignTask).where(
				CampaignTask.campaign_id == campaign_id,
				CampaignTask.account_id == account_id,
				CampaignTask.status == "pending",
			).order_by(CampaignTask.id)))

			pw = PlaywrightController(config=None)
			pw.start()
			try:
				# Keep profile open for all tasks of this account
				with pw.launch_profile(profile_path=account.profile_path) as (ctx, page):
					for task in pending:
						if self._cancelled:
							break
						self._emit("task_start", task_id=task.id, group_id=task.group_id)
						# Choose assets randomly if provided
						poster = random.choice(posters) if posters else None
						caption = random.choice(captions) if captions else None
						link = random.choice(links) if links else None
						# TODO: navigate to group URL and perform post
						time.sleep(random.uniform(0.5, 1.5))
						task.status = "done"
						s.flush()
						self._emit("task_done", task_id=task.id, poster_id=getattr(poster, "id", None), caption_id=getattr(caption, "id", None), link_id=getattr(link, "id", None))
			finally:
				pw.stop()

			self._emit("account_done", campaign_id=campaign_id, account_id=account_id)