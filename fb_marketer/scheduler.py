from __future__ import annotations

from datetime import datetime
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger


def build_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    return scheduler


def schedule_campaign(scheduler: BackgroundScheduler, campaign_id: int, run_fn: Callable[[int], None], run_at: datetime) -> None:
    scheduler.add_job(run_fn, 'date', run_date=run_at, args=[campaign_id], id=f"campaign-{campaign_id}")
    logger.info(f"Scheduled campaign {campaign_id} at {run_at}")

