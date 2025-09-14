from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class AppConfig:
	"""Application configuration and filesystem locations."""
	# Base directories
	project_root: Path = Path(__file__).resolve().parents[2]
	data_dir: Path = project_root / "data"
	logs_dir: Path = project_root / "logs"
	database_path: Path = data_dir / "app.db"

	# UI / runtime defaults
	headless: bool = False
	max_concurrent_browsers: int = 3

	# Logging
	log_level: str = "INFO"
	log_file_name: str = "app.log"

	# Crypto (placeholder; integrate key mgmt later)
	encryption_key_env: str = "APP_ENCRYPTION_KEY"

	def __post_init__(self) -> None:
		# Load environment overrides from .env if present
		load_dotenv(override=False)
		self.headless = os.getenv("APP_HEADLESS", str(self.headless)).lower() in {"1", "true", "yes"}
		self.max_concurrent_browsers = int(os.getenv("APP_MAX_CONCURRENCY", self.max_concurrent_browsers))
		self.log_level = os.getenv("APP_LOG_LEVEL", self.log_level)
		# Allow overriding storage locations
		data_dir_env = os.getenv("APP_DATA_DIR")
		logs_dir_env = os.getenv("APP_LOGS_DIR")
		db_path_env = os.getenv("APP_DB_PATH")
		if data_dir_env:
			self.data_dir = Path(data_dir_env)
		if logs_dir_env:
			self.logs_dir = Path(logs_dir_env)
		if db_path_env:
			self.database_path = Path(db_path_env)


def ensure_app_directories(config: AppConfig) -> None:
	config.data_dir.mkdir(parents=True, exist_ok=True)
	config.logs_dir.mkdir(parents=True, exist_ok=True)