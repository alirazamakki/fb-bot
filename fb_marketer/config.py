from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from dotenv import load_dotenv


class AppConfig(BaseModel):
    db_url: str
    headless: bool = False
    batch_size: int = 3
    encryption_key_file: Path
    log_level: str = "INFO"


def get_user_data_dir() -> Path:
    base = Path.home() / ".fb_marketer"
    base.mkdir(parents=True, exist_ok=True)
    (base / "profiles").mkdir(parents=True, exist_ok=True)
    (base / "logs").mkdir(parents=True, exist_ok=True)
    (base / "db").mkdir(parents=True, exist_ok=True)
    (base / "keys").mkdir(parents=True, exist_ok=True)
    return base


def load_config(dotenv_path: Optional[Path] = None) -> AppConfig:
    if dotenv_path is None:
        dotenv_path = Path.cwd() / ".env"
    load_dotenv(dotenv_path)

    user_dir = get_user_data_dir()
    default_db = f"sqlite:///{(user_dir / 'db' / 'fb_marketer.db').as_posix()}"
    db_url = os.getenv("APP_DB_URL", default_db)
    headless = os.getenv("APP_HEADLESS", "false").lower() in {"1", "true", "yes", "y"}
    batch_size = int(os.getenv("APP_BATCH_SIZE", "3"))
    key_file_env = os.getenv("APP_ENCRYPTION_KEY_FILE")
    encryption_key_file = Path(key_file_env) if key_file_env else (user_dir / "keys" / "fernet.key")
    log_level = os.getenv("APP_LOG_LEVEL", "INFO")

    return AppConfig(
        db_url=db_url,
        headless=headless,
        batch_size=batch_size,
        encryption_key_file=encryption_key_file,
        log_level=log_level,
    )

