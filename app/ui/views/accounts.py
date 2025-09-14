from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QHBoxLayout,
	QLineEdit,
	QPushButton,
	QTableWidget,
	QTableWidgetItem,
	QHeaderView,
	QMessageBox,
	QAbstractItemView,
)

from app.core.config import AppConfig
from app.services import account_service


class AccountManagerView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config
		self._name = QLineEdit()
		self._profile = QLineEdit()
		self._email = QLineEdit()
		self._add_btn = QPushButton("Add")
		self._update_btn = QPushButton("Update Selected")
		self._delete_btn = QPushButton("Delete Selected")
		self._fetch_groups_btn = QPushButton("Fetch Groups (Stub)")

		form = QHBoxLayout()
		self._name.setPlaceholderText("Account name")
		self._profile.setPlaceholderText("Chrome profile path (user-data-dir)")
		self._email.setPlaceholderText("Email or phone (optional)")
		form.addWidget(self._name)
		form.addWidget(self._profile)
		form.addWidget(self._email)
		form.addWidget(self._add_btn)
		form.addWidget(self._update_btn)
		form.addWidget(self._delete_btn)
		form.addWidget(self._fetch_groups_btn)

		self._table = QTableWidget(0, 4)
		self._table.setHorizontalHeaderLabels(["ID", "Name", "Profile Path", "Email/Phone"])
		hdr = self._table.horizontalHeader()
		hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
		hdr.setSectionResizeMode(1, QHeaderView.Stretch)
		hdr.setSectionResizeMode(2, QHeaderView.Stretch)
		hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
		self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
		self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)

		root = QVBoxLayout(self)
		root.addLayout(form)
		root.addWidget(self._table)

		self._add_btn.clicked.connect(self._on_add)
		self._update_btn.clicked.connect(self._on_update)
		self._delete_btn.clicked.connect(self._on_delete)
		self._fetch_groups_btn.clicked.connect(self._on_fetch_groups)

		self._refresh()

	def _refresh(self) -> None:
		accs = account_service.list_accounts()
		self._table.setRowCount(0)
		for acc in accs:
			row = self._table.rowCount()
			self._table.insertRow(row)
			self._table.setItem(row, 0, QTableWidgetItem(str(acc.id)))
			self._table.setItem(row, 1, QTableWidgetItem(acc.name or ""))
			self._table.setItem(row, 2, QTableWidgetItem(acc.profile_path or ""))
			self._table.setItem(row, 3, QTableWidgetItem(acc.email_or_phone or ""))

	def _selected_id(self) -> int | None:
		idxs = self._table.selectionModel().selectedRows()
		if not idxs:
			return None
		row = idxs[0].row()
		item = self._table.item(row, 0)
		return int(item.text()) if item else None

	def _on_add(self) -> None:
		name = self._name.text().strip()
		profile = self._profile.text().strip()
		email = self._email.text().strip() or None
		if not name or not profile:
			QMessageBox.warning(self, "Validation", "Name and profile path are required.")
			return
		account_service.create_account(name=name, profile_path=profile, email_or_phone=email)
		self._name.clear()
		self._profile.clear()
		self._email.clear()
		self._refresh()

	def _on_update(self) -> None:
		acc_id = self._selected_id()
		if not acc_id:
			return
		name = self._name.text().strip() or None
		profile = self._profile.text().strip() or None
		email = self._email.text().strip() or None
		try:
			account_service.update_account(acc_id, name=name, profile_path=profile, email_or_phone=email)
		except Exception as exc:  # noqa: BLE001
			QMessageBox.critical(self, "Error", str(exc))
		self._refresh()

	def _on_delete(self) -> None:
		acc_id = self._selected_id()
		if not acc_id:
			return
		account_service.delete_account(acc_id)
		self._refresh()

	def _on_fetch_groups(self) -> None:
		acc_id = self._selected_id()
		if not acc_id:
			QMessageBox.information(self, "Fetch Groups", "Select an account first.")
			return
		count = account_service.stub_fetch_groups(acc_id)
		QMessageBox.information(self, "Fetch Groups", f"Added {count} sample groups (stub).")