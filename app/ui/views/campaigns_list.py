from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QHBoxLayout,
	QPushButton,
	QListWidget,
	QListWidgetItem,
	QTextEdit,
	QMessageBox,
	QMenu,
)

from app.core.config import AppConfig
from app.services import campaign_service


class CampaignsListView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config
		self._list = QListWidget(); self._list.setContextMenuPolicy(Qt.CustomContextMenu)
		self._preview = QTextEdit(); self._preview.setReadOnly(True)
		self._refresh_btn = QPushButton("Refresh")
		self._preview_btn = QPushButton("Preview Selected")
		self._delete_btn = QPushButton("Delete Selected")

		head = QHBoxLayout()
		head.addWidget(self._refresh_btn)
		head.addWidget(self._preview_btn)
		head.addWidget(self._delete_btn)

		root = QVBoxLayout(self)
		root.addLayout(head)
		root.addWidget(self._list)
		root.addWidget(self._preview)

		self._refresh_btn.clicked.connect(self._refresh)
		self._preview_btn.clicked.connect(self._on_preview)
		self._delete_btn.clicked.connect(self._on_delete)
		self._list.customContextMenuRequested.connect(self._on_context)

		self._refresh()

	def _refresh(self) -> None:
		self._list.clear()
		for camp in campaign_service.list_campaigns():
			item = QListWidgetItem(f"#{camp.id} – {camp.name} [{camp.status}]")
			item.setData(Qt.UserRole, camp.id)
			self._list.addItem(item)

	def _selected_campaign_id(self) -> int | None:
		items = self._list.selectedItems()
		if not items:
			return None
		return int(items[0].data(Qt.UserRole))

	def _on_preview(self) -> None:
		cid = self._selected_campaign_id()
		if not cid:
			return
		tasks = campaign_service.list_campaign_tasks(cid)
		lines = [f"Task {t.id}: account={t.account_id} group={t.group_id} status={t.status}" for t in tasks]
		self._preview.setText("\n".join(lines) or "No tasks")

	def _on_delete(self) -> None:
		cid = self._selected_campaign_id()
		if not cid:
			return
		res = QMessageBox.question(self, "Delete Campaign", f"Delete campaign #{cid}? This removes its tasks.")
		if res == QMessageBox.Yes:
			campaign_service.delete_campaign(cid)
			self._preview.clear()
			self._refresh()

	def _on_context(self, pos) -> None:
		item = self._list.itemAt(pos)
		if not item:
			return
		cid = int(item.data(Qt.UserRole))
		menu = QMenu(self)
		act_preview = menu.addAction("Preview")
		act_delete = menu.addAction("Delete")
		chosen = menu.exec(self._list.mapToGlobal(pos))
		if chosen == act_preview:
			self._list.setCurrentItem(item)
			self._on_preview()
		elif chosen == act_delete:
			self._list.setCurrentItem(item)
			self._on_delete()