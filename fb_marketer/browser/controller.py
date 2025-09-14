from __future__ import annotations

from contextlib import contextmanager
from typing import Optional, Dict, Any, Tuple

from loguru import logger
from playwright.sync_api import sync_playwright, BrowserContext, Page, Playwright


def _build_proxy_config(proxy: Optional[Dict[str, Any]]) -> Optional[Dict[str, str]]:
    if not proxy:
        return None
    server = proxy.get("server") or proxy.get("host")
    if not server:
        return None
    if proxy.get("port") and ":" not in str(server):
        server = f"{server}:{proxy['port']}"
    result: Dict[str, str] = {"server": str(server)}
    if proxy.get("username"):
        result["username"] = str(proxy["username"])
    if proxy.get("password"):
        result["password"] = str(proxy["password"])
    return result


@contextmanager
def launch_persistent_profile(profile_path: str, headless: bool = False, proxy: Optional[Dict[str, Any]] = None):
    pw: Optional[Playwright] = None
    context: Optional[BrowserContext] = None
    try:
        pw = sync_playwright().start()
        launch_options = {
            "user_data_dir": profile_path,
            "headless": headless,
            "args": ["--disable-dev-shm-usage"],
        }
        proxy_cfg = _build_proxy_config(proxy)
        if proxy_cfg:
            launch_options["proxy"] = proxy_cfg
        context = pw.chromium.launch_persistent_context(**launch_options)
        page: Page = context.new_page()
        yield pw, context, page
    finally:
        try:
            if context:
                context.close()
        except Exception as e:
            logger.warning(f"Error closing context: {e}")
        try:
            if pw:
                pw.stop()
        except Exception as e:
            logger.warning(f"Error stopping Playwright: {e}")

