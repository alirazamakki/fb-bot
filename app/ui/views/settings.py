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
		self._theme = QLineEdit(); self._theme.setPlaceholderText("qt-material theme (e.g., dark_teal.xml)")
		self._apply_theme = QPushButton("Apply Theme")
		self._save = QPushButton("Save (session)")

		row1 = QHBoxLayout(); row1.addWidget(self._batch); row1.addWidget(self._delay_min); row1.addWidget(self._delay_max)
		row2 = QHBoxLayout(); row2.addWidget(self._poster_cols); row2.addWidget(self._caption_cols)
		row3 = QHBoxLayout(); row3.addWidget(self._theme); row3.addWidget(self._apply_theme); row3.addWidget(self._save)
		root = QVBoxLayout(self)
		root.addLayout(row1)
		root.addLayout(row2)
		root.addLayout(row3)
		self._apply_theme.clicked.connect(self._on_apply_theme)
		self._save.clicked.connect(self._on_save)

	def _on_apply_theme(self) -> None:
		try:
			from qt_material import apply_stylesheet
		except Exception:
			QMessageBox.warning(self, "Theme", "qt-material not installed.")
			return
		name = self._theme.text().strip() or self._config.theme_name
		try:
			apply_stylesheet(self.window().windowHandle().screen().virtualSiblings()[0].virtualSiblings()[0].context().application(), theme=name)  # type: ignore[attr-defined]
		except Exception:
			# fallback: apply to QApplication.instance
			from PySide6.QtWidgets import QApplication
			try:
				apply_stylesheet(QApplication.instance(), theme=name)
			except Exception as exc:
				QMessageBox.warning(self, "Theme", f"Failed to apply theme: {exc}")
				return
		self._config.theme_name = name
		QMessageBox.information(self, "Theme", f"Applied theme: {name}")

	def _on_save(self) -> None:
		try:
			if self._batch.text().strip():
				self._config.max_concurrent_browsers = int(self._batch.text().strip())
			if self._poster_cols.text().strip():
				self._config.poster_grid_cols = int(self._poster_cols.text().strip())
			if self._caption_cols.text().strip():
				self._config.caption_grid_cols = int(self._caption_cols.text().strip())
			if self._theme.text().strip():
				self._config.theme_name = self._theme.text().strip()
			QMessageBox.information(self, "Settings", "Saved for session.")
		except ValueError:
			QMessageBox.warning(self, "Settings", "Invalid number.")