from __future__ import annotations

import random
import time
from typing import Optional

from loguru import logger
from sqlalchemy.orm import Session

from fb_marketer.browser.controller import launch_persistent_profile
from fb_marketer.config import load_config
from fb_marketer.core.utils import build_caption, choose_weighted_link, WeightedLink
from fb_marketer.db import SessionLocal
from fb_marketer.db.models import Account, Group, Caption, Link, Poster


def run_account_job(account_id: int) -> None:
    cfg = load_config()
    with SessionLocal() as session:  # type: Session
        account: Optional[Account] = session.get(Account, account_id)
        if not account:
            logger.warning(f"Account {account_id} not found")
            return

        proxy_cfg = None  # integrate with Proxy model if needed
        with launch_persistent_profile(account.profile_path, headless=cfg.headless, proxy=proxy_cfg) as (_, context, page):
            groups = session.query(Group).filter_by(account_id=account.id, excluded=False).all()
            posters = session.query(Poster).all()
            captions = session.query(Caption).all()
            links = [WeightedLink(id=l.id, url=l.url, weight=l.weight) for l in session.query(Link).all()]

            if not groups:
                logger.info(f"Account {account.name} has no groups to process")
                return

            for grp in groups:
                link = choose_weighted_link(links)
                link_url = link.url if link else None
                caption_tpl = captions[0].text if captions else "{LINK}"
                caption = build_caption(caption_tpl, link_url, grp.name)
                poster_path = posters[0].filepath if posters else None

                try:
                    logger.info(f"[Dry-run] Would post to {grp.name} with link={link_url} caption_len={len(caption)} poster={poster_path}")
                    # TODO: Implement actual post flow safely using the page
                    # e.g., navigate to grp.url, find composer, attach image, set caption, click post.
                except Exception as exc:
                    logger.exception(f"Error posting to group {grp.name}: {exc}")
                finally:
                    delay = random.uniform(3, 6)
                    time.sleep(delay)

