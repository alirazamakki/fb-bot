from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QHBoxLayout,
	QComboBox,
	QLineEdit,
	QPushButton,
	QTableWidget,
	QTableWidgetItem,
	QHeaderView,
	QMessageBox,
)

from app.core.config import AppConfig
from app.services import account_service


class GroupManagerView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config

		self._account = QComboBox()
		self._name = QLineEdit()
		self._url = QLineEdit()
		self._add_btn = QPushButton("Add Group")
		self._del_btn = QPushButton("Delete Selected")

		self._name.setPlaceholderText("Group name")
		self._url.setPlaceholderText("Group URL")

		head = QHBoxLayout()
		head.addWidget(self._account)
		head.addWidget(self._name)
		head.addWidget(self._url)
		head.addWidget(self._add_btn)
		head.addWidget(self._del_btn)

		self._table = QTableWidget(0, 4)
		self._table.setHorizontalHeaderLabels(["ID", "FB Group ID", "Name", "URL"])
		hdr = self._table.horizontalHeader()
		hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
		hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
		hdr.setSectionResizeMode(2, QHeaderView.Stretch)
		hdr.setSectionResizeMode(3, QHeaderView.Stretch)

		root = QVBoxLayout(self)
		root.addLayout(head)
		root.addWidget(self._table)

		self._account.currentIndexChanged.connect(self._refresh)
		self._add_btn.clicked.connect(self._on_add)
		self._del_btn.clicked.connect(self._on_delete)

		self._load_accounts()

	def _load_accounts(self) -> None:
		self._account.clear()
		accs = account_service.list_accounts()
		for acc in accs:
			self._account.addItem(f"{acc.id} – {acc.name}", acc.id)
		self._refresh()

	def _current_account_id(self) -> int | None:
		idx = self._account.currentIndex()
		if idx < 0:
			return None
		return int(self._account.currentData())

	def _refresh(self) -> None:
		acc_id = self._current_account_id()
		self._table.setRowCount(0)
		if not acc_id:
			return
		groups = account_service.list_groups_for_account(acc_id)
		for g in groups:
			row = self._table.rowCount()
			self._table.insertRow(row)
			self._table.setItem(row, 0, QTableWidgetItem(str(g.id)))
			self._table.setItem(row, 1, QTableWidgetItem(g.fb_group_id or ""))
			self._table.setItem(row, 2, QTableWidgetItem(g.name or ""))
			self._table.setItem(row, 3, QTableWidgetItem(g.url or ""))

	def _on_add(self) -> None:
		acc_id = self._current_account_id()
		if not acc_id:
			QMessageBox.information(self, "Add Group", "Please select an account.")
			return
		name = self._name.text().strip()
		url = self._url.text().strip()
		if not name or not url:
			QMessageBox.warning(self, "Validation", "Name and URL are required.")
			return
		account_service.create_group(acc_id, name=name, url=url)
		self._name.clear()
		self._url.clear()
		self._refresh()

	def _on_delete(self) -> None:
		rows = self._table.selectionModel().selectedRows()
		if not rows:
			return
		for r in rows:
			gid_item = self._table.item(r.row(), 0)
			if gid_item:
				account_service.delete_group(int(gid_item.text()))
		self._refresh()