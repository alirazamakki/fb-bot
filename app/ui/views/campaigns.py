from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QHBoxLayout,
	QLineEdit,
	QPushButton,
	QListWidget,
	QListWidgetItem,
	QMessageBox,
)

from app.core.config import AppConfig
from app.services import account_service, campaign_service


class CampaignBuilderView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config

		self._name = QLineEdit()
		self._name.setPlaceholderText("Campaign name")
		self._create_btn = QPushButton("Create Campaign (all groups of selected accounts)")

		self._accounts = QListWidget()
		self._accounts.setSelectionMode(QListWidget.MultiSelection)

		top = QHBoxLayout()
		top.addWidget(self._name)
		top.addWidget(self._create_btn)

		root = QVBoxLayout(self)
		root.addLayout(top)
		root.addWidget(self._accounts)

		self._create_btn.clicked.connect(self._on_create)
		self._refresh_accounts()

	def _refresh_accounts(self) -> None:
		self._accounts.clear()
		for acc in account_service.list_accounts():
			item = QListWidgetItem(f"{acc.id} – {acc.name}")
			item.setData(Qt.UserRole, acc.id)
			self._accounts.addItem(item)

	def _on_create(self) -> None:
		name = self._name.text().strip()
		if not name:
			QMessageBox.warning(self, "Validation", "Campaign name is required.")
			return
		selected_ids = [i.data(Qt.UserRole) for i in self._accounts.selectedItems()]
		if not selected_ids:
			QMessageBox.warning(self, "Validation", "Select at least one account.")
			return
		config = {
			"delay_min": 5,
			"delay_max": 10,
			"batch_size": 2,
			"rotation_mode": "random",
		}
		camp = campaign_service.create_campaign(name=name, config=config, account_ids=selected_ids)
		QMessageBox.information(self, "Campaign Created", f"Created campaign #{camp.id} with tasks.")
		self._name.clear()