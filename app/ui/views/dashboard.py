from __future__ import annotations

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton

from app.core.config import AppConfig
from app.core.db import db_session
from app.core.models import Account, Group, Campaign, CampaignTask


class DashboardView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._label = QLabel()
		self._refresh_btn = QPushButton("Refresh")
		layout = QVBoxLayout(self)
		layout.addWidget(self._label)
		layout.addWidget(self._refresh_btn)
		self._refresh_btn.clicked.connect(self._refresh)
		self._refresh()

	def _refresh(self) -> None:
		with db_session() as s:
			acc = s.query(Account).count()
			grp = s.query(Group).count()
			cmp = s.query(Campaign).count()
			tsk = s.query(CampaignTask).count()
		self._label.setText(f"Accounts: {acc}\nGroups: {grp}\nCampaigns: {cmp}\nTasks: {tsk}")