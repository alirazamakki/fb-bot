from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.core.config import AppConfig, ensure_app_directories
from app.core.logger import configure_logging
from app.core.db import initialize_database
from app.ui.main_window import MainWindow


def main() -> None:
	"""Application entrypoint: configure, init subsystems, start UI."""
	# Ensure deterministic working directory when started as module or exe
	if getattr(sys, "frozen", False):  # PyInstaller
		base_dir = Path(sys._MEIPASS)  # type: ignore[attr-defined]
	else:
		base_dir = Path(__file__).resolve().parent.parent

	# Load configuration and prepare directories
	config = AppConfig()
	ensure_app_directories(config)

	# Configure logging early
	configure_logging(config)

	# Initialize database (models to be added later)
	initialize_database(config)

	# Start Qt application
	app = QApplication(sys.argv)
	app.setApplicationName("FB Group Campaign Manager")

	# Apply theme if available
	try:
		from qt_material import apply_stylesheet
		apply_stylesheet(app, theme=config.theme_name)
	except Exception:
		pass

	window = MainWindow(config=config)
	window.show()

	sys.exit(app.exec())


if __name__ == "__main__":
	main()