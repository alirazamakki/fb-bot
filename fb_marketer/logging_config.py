from __future__ import annotations

from pathlib import Path
from loguru import logger

from fb_marketer.config import get_user_data_dir


def configure_logging(level: str = "INFO") -> Path:
    logs_dir = get_user_data_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "app.log"

    logger.remove()
    logger.add(
        log_file.as_posix(),
        rotation="10 MB",
        retention="10 days",
        level=level,
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} | {message}",
    )
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=level,
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{message}</cyan>",
    )
    return log_file

