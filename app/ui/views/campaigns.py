from __future__ import annotations

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from app.core.config import AppConfig


class CampaignBuilderView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		layout = QVBoxLayout(self)
		layout.addWidget(QLabel("Campaign Builder – select accounts, assets, and options"))