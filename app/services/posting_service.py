from __future__ import annotations

import re
import time
from typing import Optional
from datetime import datetime
from pathlib import Path

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
	_clicked = (
		_try_click(page, name="Photo") or
		_try_click(page, name="Photo/video") or
		_try_click(page, name="Add photo") or
		_try_click(page, name="Add Photos")
	)
	try:
		file_input = page.locator("input[type=file]").first
		file_input.set_input_files(poster_path, timeout=12000)
	except Exception:
		logger.warning("Could not find file input to attach poster")


def _scroll_down(page: Page, times: int = 2) -> None:
	for _ in range(times):
		try:
			page.mouse.wheel(0, 800)
		except Exception:
			pass
		time.sleep(0.4)


def _open_composer(page: Page, timeout_s: int) -> bool:
	# Try switching to Discussion tab first
	for lbl in ["Discussion", "Posts", "Featured"]:
		try:
			page.get_by_role("link", name=re.compile(lbl, re.I)).first.click(timeout=2000)
			page.wait_for_load_state("networkidle", timeout=3000)
		except Exception:
			pass
	# Scroll a bit so the composer placeholder is in view
	_scroll_down(page, times=3)
	# Prefer exact placeholder first
	try:
		box = page.get_by_placeholder("Write something...").first
		box.click(timeout=timeout_s * 1000)
		# Wait for a contenteditable area to appear in the popup/composer
		page.locator('[contenteditable="true"]').first.wait_for(timeout=timeout_s * 1000)
		return True
	except Exception:
		pass
	# Fallback candidates
	candidates = [
		lambda: page.get_by_placeholder(re.compile("Write.*|What's on your mind|Write something", re.I)).first,
		lambda: page.get_by_role("textbox").first,
		lambda: page.get_by_text(re.compile("Write something|Start discussion|Post", re.I)).first,
	]
	for getter in candidates:
		try:
			el = getter()
			el.click(timeout=timeout_s * 1000)
			page.locator('[contenteditable="true"]').first.wait_for(timeout=timeout_s * 1000)
			return True
		except Exception:
			continue
	return False


def _save_debug(page: Page, note: str) -> None:
	try:
		logs = Path("logs"); logs.mkdir(exist_ok=True)
		stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
		png = logs / f"fb_debug_{stamp}.png"
		html = logs / f"fb_debug_{stamp}.html"
		page.screenshot(path=str(png), full_page=True)
		html.write_text(page.content())
		logger.error(f"Saved debug artifacts: {png} {html} ({note})")
	except Exception:
		pass


def post_to_group(page: Page, group_url: str, caption_text: str, poster_path: Optional[str], *, timeout_s: int = 60) -> bool:
	logger.info(f"Navigating to group {group_url}")
	page.goto(group_url, wait_until="load")
	try:
		page.wait_for_load_state("networkidle", timeout=timeout_s * 1000)
	except PlaywrightTimeoutError:
		pass
	# Open composer via explicit scroll -> click "Write something..."
	if not _open_composer(page, timeout_s):
		_save_debug(page, "composer_not_open")
		raise RuntimeError("Could not open post composer")
	# Fill caption
	try:
		editable = page.locator('[contenteditable="true"]').first
		editable.click()
		editable.type(caption_text, delay=10)
	except Exception:
		logger.warning("Editable not found, typing to page")
		page.keyboard.type(caption_text, delay=10)
	# Attach image
	_attach_image_if_any(page, poster_path)
	# Click Post / Share
	clicked_post = _try_click(page, name="Post") or _try_click(page, name="Share now") or _try_click(page, name="Post now")
	if not clicked_post:
		_save_debug(page, "post_button_not_found")
		raise RuntimeError("Could not find Post button")
	try:
		page.wait_for_load_state("networkidle", timeout=timeout_s * 1000)
	except PlaywrightTimeoutError:
		pass
	return True