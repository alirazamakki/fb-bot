from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QHBoxLayout, QLineEdit, QComboBox

from app.core.config import AppConfig


class LogsView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config
		self._box = QTextEdit(); self._box.setReadOnly(True)
		self._refresh = QPushButton("Refresh")
		self._filter_text = QLineEdit(); self._filter_text.setPlaceholderText("Filter text…")
		self._filter_level = QComboBox(); self._filter_level.addItems(["ALL", "INFO", "WARNING", "ERROR"]) 
		row = QHBoxLayout(); row.addWidget(self._refresh); row.addWidget(self._filter_level); row.addWidget(self._filter_text)
		root = QVBoxLayout(self)
		root.addLayout(row)
		root.addWidget(self._box)
		self._refresh.clicked.connect(self._on_refresh)
		self._filter_text.textChanged.connect(self._on_refresh)
		self._filter_level.currentIndexChanged.connect(self._on_refresh)
		self._on_refresh()

	def _on_refresh(self) -> None:
		log_file = Path(self._config.logs_dir) / self._config.log_file_name
		if not log_file.exists():
			self._box.setPlainText("No logs yet.")
			return
		needle = self._filter_text.text().strip().lower()
		level = self._filter_level.currentText()
		lines = []
		for ln in log_file.read_text(errors="ignore").splitlines():
			low = ln.lower()
			if needle and needle not in low:
				continue
			if level != "ALL":
				if f"| {level}" not in ln and f"[{level}]" not in ln:
					continue
			lines.append(ln)
		self._box.setPlainText("\n".join(lines) if lines else "No matching logs.")