from __future__ import annotations

from dataclasses import dataclass

from app.core.config import AppConfig


@dataclass
class AppContext:
	config: AppConfig