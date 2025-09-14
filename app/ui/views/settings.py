from __future__ import annotations

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QMessageBox

from app.core.config import AppConfig


class SettingsView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config
		self._batch = QLineEdit(); self._batch.setPlaceholderText("Default batch size")
		self._delay_min = QLineEdit(); self._delay_min.setPlaceholderText("Default delay min")
		self._delay_max = QLineEdit(); self._delay_max.setPlaceholderText("Default delay max")
		self._save = QPushButton("Save (session)")

		row = QHBoxLayout(); row.addWidget(self._batch); row.addWidget(self._delay_min); row.addWidget(self._delay_max); row.addWidget(self._save)
		root = QVBoxLayout(self)
		root.addLayout(row)
		self._save.clicked.connect(self._on_save)

	def _on_save(self) -> None:
		try:
			self._config.max_concurrent_browsers = int(self._batch.text().strip() or self._config.max_concurrent_browsers)
			# We reuse these as defaults when building config
			QMessageBox.information(self, "Settings", "Saved for session.")
		except ValueError:
			QMessageBox.warning(self, "Settings", "Invalid number.")