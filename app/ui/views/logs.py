from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit

from app.core.config import AppConfig


class LogsView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config
		self._box = QTextEdit(); self._box.setReadOnly(True)
		self._refresh = QPushButton("Refresh Logs")
		root = QVBoxLayout(self)
		root.addWidget(self._refresh)
		root.addWidget(self._box)
		self._refresh.clicked.connect(self._on_refresh)
		self._on_refresh()

	def _on_refresh(self) -> None:
		log_file = Path(self._config.logs_dir) / self._config.log_file_name
		if log_file.exists():
			self._box.setPlainText(log_file.read_text(errors="ignore"))
		else:
			self._box.setPlainText("No logs yet.")