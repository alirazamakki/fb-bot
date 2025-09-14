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
		self._poster_cols = QLineEdit(); self._poster_cols.setPlaceholderText("Poster grid columns")
		self._caption_cols = QLineEdit(); self._caption_cols.setPlaceholderText("Caption grid columns")
		self._save = QPushButton("Save (session)")

		row1 = QHBoxLayout(); row1.addWidget(self._batch); row1.addWidget(self._delay_min); row1.addWidget(self._delay_max)
		row2 = QHBoxLayout(); row2.addWidget(self._poster_cols); row2.addWidget(self._caption_cols); row2.addWidget(self._save)
		root = QVBoxLayout(self)
		root.addLayout(row1)
		root.addLayout(row2)
		self._save.clicked.connect(self._on_save)

	def _on_save(self) -> None:
		try:
			if self._batch.text().strip():
				self._config.max_concurrent_browsers = int(self._batch.text().strip())
			if self._poster_cols.text().strip():
				self._config.poster_grid_cols = int(self._poster_cols.text().strip())
			if self._caption_cols.text().strip():
				self._config.caption_grid_cols = int(self._caption_cols.text().strip())
			QMessageBox.information(self, "Settings", "Saved for session.")
		except ValueError:
			QMessageBox.warning(self, "Settings", "Invalid number.")