from __future__ import annotations

import random
import time
from typing import Callable, Iterable, List, Optional, Tuple

from sqlalchemy import select

from app.core.queue_manager import PoolManager, WorkerTask
from app.core.db import db_session
from app.core.models import Campaign, CampaignTask, Account, Group, Poster, Caption, Link, Proxy
from app.core.playwright_controller import PlaywrightController
from app.services.posting_service import post_to_group, build_caption

ProgressCallback = Callable[[str, dict], None]


def _choose_rotating(items: list, mode: str, last_idx: Optional[int]) -> Tuple[Optional[object], Optional[int]]:
	if not items:
		return None, last_idx
	if mode == "round_robin":
		next_idx = 0 if last_idx is None else (last_idx + 1) % len(items)
		return items[next_idx], next_idx
	# default random but avoid immediate repeat
	choices = list(range(len(items)))
	if last_idx is not None and len(items) > 1:
		choices.remove(last_idx)
	idx = random.choice(choices)
	return items[idx], idx


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
			dry_run = bool(config.get("dry_run", False))
			max_retries = int(config.get("retries", 2))
			rotation_mode = str(config.get("rotation_mode", "random"))
			poster_ids = config.get("poster_ids") or []
			caption_ids = config.get("caption_ids") or []
			link_ids = config.get("link_ids") or []
			priority_link_ids = set(config.get("link_priority_ids") or [])
			blacklist_link_ids = set(config.get("link_blacklist_ids") or [])
			delay_min = int(config.get("delay_min", 5))
			delay_max = int(config.get("delay_max", 10))

			# Prefetch assets into memory for selection
			posters = list(s.scalars(select(Poster).where(Poster.id.in_(poster_ids)))) if poster_ids else []
			captions = list(s.scalars(select(Caption).where(Caption.id.in_(caption_ids)))) if caption_ids else []
			links_all = list(s.scalars(select(Link).where(Link.id.in_(link_ids)))) if link_ids else []
			# Apply blacklist/priority
			if priority_link_ids:
				links = [l for l in links_all if l.id in priority_link_ids]
				if not links:
					links = links_all
			else:
				links = links_all
			if blacklist_link_ids:
				links = [l for l in links if l.id not in blacklist_link_ids]

			self._emit("account_start", campaign_id=campaign_id, account_id=account_id, account_name=account.name)

			pending = list(s.scalars(select(CampaignTask).where(
				CampaignTask.campaign_id == campaign_id,
				CampaignTask.account_id == account_id,
				CampaignTask.status == "pending",
			).order_by(CampaignTask.id)))

			# Prepare rotation indices to avoid repeats
			last_poster_idx: Optional[int] = None
			last_caption_idx: Optional[int] = None
			last_link_idx: Optional[int] = None

			# Proxy settings if any
			proxy_dict = None
			if account.proxy_id:
				proxy = s.get(Proxy, account.proxy_id)
				if proxy:
					server = ("socks5://" if proxy.type and "sock" in proxy.type.lower() else "http://") + f"{proxy.host}:{proxy.port}"
					proxy_dict = {"server": server}
					if proxy.username:
						proxy_dict["username"] = proxy.username
					if proxy.password:
						proxy_dict["password"] = proxy.password

			pw = PlaywrightController(config=None)
			pw.start()
			try:
				with pw.launch_profile(profile_path=account.profile_path, proxy=proxy_dict) as (ctx, page):
					for task in pending:
						if self._cancelled:
							break
						self._emit("task_start", task_id=task.id, group_id=task.group_id)
						poster_obj, last_poster_idx = _choose_rotating(posters, rotation_mode, last_poster_idx)
						caption_obj, last_caption_idx = _choose_rotating(captions, rotation_mode, last_caption_idx)
						link_obj, last_link_idx = _choose_rotating(links, rotation_mode, last_link_idx)
						caption_text = caption_obj.text if caption_obj else ""
						link_url = link_obj.url if link_obj else None
						group = s.get(Group, task.group_id)
						group_url = group.url if group and group.url else "https://www.facebook.com/groups"
						cap_text = build_caption(caption_text, link_url, group.name if group else None)
						poster_path = poster_obj.filepath if poster_obj else None

						ok = True
						if not dry_run:
							attempt = 0
							ok = False
							while attempt <= max_retries and not ok and not self._cancelled:
								attempt += 1
								try:
									ok = post_to_group(page, group_url, cap_text, poster_path)
								except Exception as exc:  # noqa: BLE001
									self._emit("task_error", task_id=task.id, error=str(exc), attempt=attempt)
									time.sleep(min(60, 2 ** attempt))
						else:
							# Dry run: simulate success
							time.sleep(0.5)

						task.status = "done" if ok else "failed"
						s.flush()
						self._emit("task_done", task_id=task.id, success=(task.status == "done"), poster_id=getattr(poster_obj, "id", None), caption_id=getattr(caption_obj, "id", None), link_id=getattr(link_obj, "id", None))
			finally:
				pw.stop()

			self._emit("account_done", campaign_id=campaign_id, account_id=account_id)