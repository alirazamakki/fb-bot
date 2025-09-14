from __future__ import annotations

from pathlib import Path
from typing import Optional

from loguru import logger

from app.core.config import AppConfig


_CONFIGURED = False


def configure_logging(config: AppConfig) -> None:
	global _CONFIGURED
	if _CONFIGURED:
		return

	logger.remove()  # Remove default stderr handler to re-add with level
	logger.add(
		lambda msg: print(msg, end=""),
		level=config.log_level,
		colorize=True,
		backtrace=False,
		diagnose=False,
	)

	log_file: Path = config.logs_dir / config.log_file_name
	logger.add(
		str(log_file),
		rotation="10 MB",
		retention=5,
		compression="zip",
		enqueue=True,
		level=config.log_level,
		backtrace=False,
		diagnose=False,
		format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
	)

	_CONFIGURED = True