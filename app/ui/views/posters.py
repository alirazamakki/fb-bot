from __future__ import annotations

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from app.core.config import AppConfig


class PosterLibraryView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		layout = QVBoxLayout(self)
		layout.addWidget(QLabel("Poster Library – upload and categorize images"))