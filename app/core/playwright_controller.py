from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional

from playwright.sync_api import sync_playwright, BrowserContext, Page, Playwright

from app.core.config import AppConfig


class PlaywrightController:
	"""Helper to manage a persistent Chromium context per account profile."""

	def __init__(self, config: Optional[AppConfig]) -> None:
		self._config = config
		self._pw: Optional[Playwright] = None

	def start(self) -> None:
		if self._pw is None:
			self._pw = sync_playwright().start()

	def stop(self) -> None:
		if self._pw is not None:
			self._pw.stop()
			self._pw = None

	@contextmanager
	def launch_profile(self, profile_path: str, proxy: Optional[dict] = None) -> Iterator[tuple[BrowserContext, Page]]:
		"""Launch persistent context for a given user-data-dir and yield (context, page)."""
		if self._pw is None:
			self.start()
		assert self._pw is not None

		args = ["--disable-dev-shm-usage"]
		headless = False if self._config is None else self._config.headless
		launch_opts = dict(
			user_data_dir=profile_path,
			headless=headless,
			args=args,
		)
		if proxy:
			launch_opts["proxy"] = {
				"server": proxy.get("server"),
				"username": proxy.get("username"),
				"password": proxy.get("password"),
			}
		context = self._pw.chromium.launch_persistent_context(**launch_opts)
		page = context.new_page()
		try:
			yield context, page
		finally:
			context.close()