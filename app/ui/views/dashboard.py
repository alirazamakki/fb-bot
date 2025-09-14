from __future__ import annotations

from typing import List

from PySide6.QtWidgets import (
	QWidget,
	QLabel,
	QVBoxLayout,
	QHBoxLayout,
	QPushButton,
	QGroupBox,
	QFormLayout,
	QListWidget,
	QListWidgetItem,
	QTextEdit,
)

from app.core.config import AppConfig
from app.core.db import db_session
from app.core.models import Account, Group, Campaign, CampaignTask, LogEntry


class DashboardView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config

		# Overview cards
		self._overview_box = QGroupBox("Overview")
		self._overview_form = QFormLayout(self._overview_box)
		self._lbl_accounts = QLabel("0")
		self._lbl_groups = QLabel("0")
		self._lbl_campaigns = QLabel("0")
		self._lbl_tasks_total = QLabel("0")
		self._lbl_tasks_pending = QLabel("0")
		self._lbl_tasks_running = QLabel("0")
		self._lbl_tasks_done = QLabel("0")
		self._lbl_tasks_failed = QLabel("0")
		self._overview_form.addRow("Accounts", self._lbl_accounts)
		self._overview_form.addRow("Groups", self._lbl_groups)
		self._overview_form.addRow("Campaigns", self._lbl_campaigns)
		self._overview_form.addRow("Tasks (total)", self._lbl_tasks_total)
		self._overview_form.addRow("Tasks (pending)", self._lbl_tasks_pending)
		self._overview_form.addRow("Tasks (running)", self._lbl_tasks_running)
		self._overview_form.addRow("Tasks (done)", self._lbl_tasks_done)
		self._overview_form.addRow("Tasks (failed)", self._lbl_tasks_failed)

		# Recent campaigns
		self._campaigns_box = QGroupBox("Recent Campaigns")
		self._campaigns_list = QListWidget()
		c_layout = QVBoxLayout(self._campaigns_box)
		c_layout.addWidget(self._campaigns_list)

		# Recent logs
		self._logs_box = QGroupBox("Recent Logs")
		self._logs = QTextEdit(); self._logs.setReadOnly(True)
		l_layout = QVBoxLayout(self._logs_box)
		l_layout.addWidget(self._logs)

		# Actions
		self._reload_btn = QPushButton("Reload")
		self._reload_btn.clicked.connect(self._refresh)

		# Layout
		top = QHBoxLayout()
		top.addWidget(self._overview_box, 1)
		top.addWidget(self._campaigns_box, 1)
		root = QVBoxLayout(self)
		root.addLayout(top)
		root.addWidget(self._logs_box, 1)
		root.addWidget(self._reload_btn)

		self._refresh()

	def _refresh(self) -> None:
		with db_session() as s:
			accounts = s.query(Account).count()
			groups = s.query(Group).count()
			campaigns = s.query(Campaign).count()
			tasks_total = s.query(CampaignTask).count()
			pending = s.query(CampaignTask).filter(CampaignTask.status == "pending").count()
			running = s.query(CampaignTask).filter(CampaignTask.status == "running").count()
			done = s.query(CampaignTask).filter(CampaignTask.status == "done").count()
			failed = s.query(CampaignTask).filter(CampaignTask.status == "failed").count()

			self._lbl_accounts.setText(str(accounts))
			self._lbl_groups.setText(str(groups))
			self._lbl_campaigns.setText(str(campaigns))
			self._lbl_tasks_total.setText(str(tasks_total))
			self._lbl_tasks_pending.setText(str(pending))
			self._lbl_tasks_running.setText(str(running))
			self._lbl_tasks_done.setText(str(done))
			self._lbl_tasks_failed.setText(str(failed))

			# Recent campaigns (last 10)
			self._campaigns_list.clear()
			for camp in s.query(Campaign).order_by(Campaign.id.desc()).limit(10):
				item = QListWidgetItem(f"#{camp.id} – {camp.name} [{camp.status}]")
				self._campaigns_list.addItem(item)

			# Recent logs (last 200 lines)
			logs = s.query(LogEntry).order_by(LogEntry.id.desc()).limit(200).all()
			lines = [f"{le.timestamp} [{le.level}] {le.message}" for le in reversed(logs)]
			self._logs.setPlainText("\n".join(lines) if lines else "No logs yet.")