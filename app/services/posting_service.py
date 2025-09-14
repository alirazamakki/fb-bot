from __future__ import annotations

import re
import time
from typing import Optional

from loguru import logger
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


def build_caption(template: Optional[str], link_url: Optional[str], group_name: Optional[str]) -> str:
	text = template or ""
	if link_url:
		text = text.replace("{LINK}", link_url)
	if group_name:
		text = text.replace("{GROUP}", group_name)
	return text


def _try_click(page: Page, *, name: str, timeout_ms: int = 5000) -> bool:
	try:
		page.get_by_role("button", name=re.compile(name, re.I)).first.click(timeout=timeout_ms)
		return True
	except Exception:
		return False


def _attach_image_if_any(page: Page, poster_path: Optional[str]) -> None:
	if not poster_path:
		return
	# Try to reveal file input via common UI entry points
	_clicked = (
		_try_click(page, name="Photo") or
		_try_click(page, name="Photo/video") or
		_try_click(page, name="Add photo")
	)
	# Try to find a file input and attach
	try:
		file_input = page.locator("input[type=file]").first
		file_input.set_input_files(poster_path, timeout=5000)
	except Exception:
		logger.warning("Could not find file input to attach poster")


def post_to_group(page: Page, group_url: str, caption_text: str, poster_path: Optional[str], *, timeout_s: int = 30) -> bool:
	logger.info(f"Navigating to group {group_url}")
	page.goto(group_url, wait_until="load")
	# Wait for composer; heuristics using placeholder/text
	composer_opened = False
	try:
		# Click into the composer area by placeholder or prompt text
		area = page.get_by_placeholder(re.compile("Write something|What's on your mind|Write something...", re.I)).first
		area.click(timeout=timeout_s * 1000)
		composer_opened = True
	except Exception:
		# Fallback: click any element that looks like a composer prompt
		try:
			page.get_by_text(re.compile("Write something|Start discussion|Post", re.I)).first.click(timeout=timeout_s * 1000)
			composer_opened = True
		except Exception:
			composer_opened = False

	if not composer_opened:
		raise RuntimeError("Could not open post composer")

	# Fill caption
	try:
		editable = page.locator('[contenteditable="true"]').first
		editable.fill("")
		editable.type(caption_text, delay=10)
	except Exception:
		logger.warning("Falling back to keyboard paste for caption")
		page.keyboard.type(caption_text, delay=10)

	# Attach image if provided
	_attach_image_if_any(page, poster_path)

	# Try to click Post
	clicked_post = _try_click(page, name="Post") or _try_click(page, name="Share now")
	if not clicked_post:
		raise RuntimeError("Could not find Post button")

	# Wait briefly for post to appear / network settles
	try:
		page.wait_for_load_state("networkidle", timeout=timeout_s * 1000)
	except PlaywrightTimeoutError:
		pass

	# Heuristic: if no error dialogs and we returned, consider success
	return True