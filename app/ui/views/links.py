from __future__ import annotations

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
)

from app.core.config import AppConfig
from app.services import library_service


class LinkManagerView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config
		self._url = QLineEdit(); self._url.setPlaceholderText("Link URL")
		self._category = QLineEdit(); self._category.setPlaceholderText("Category (optional)")
		self._weight = QLineEdit(); self._weight.setPlaceholderText("Weight (int)")
		self._add = QPushButton("Add Link")
		self._del = QPushButton("Delete Selected")
		self._filter = QLineEdit(); self._filter.setPlaceholderText("Filter category")

		head = QHBoxLayout();
		head.addWidget(self._url); head.addWidget(self._category); head.addWidget(self._weight); head.addWidget(self._add); head.addWidget(self._del)

		root = QVBoxLayout(self)
		root.addLayout(head)
		root.addWidget(self._filter)

		self._table = QTableWidget(0, 4)
		self._table.setHorizontalHeaderLabels(["ID", "URL", "Category", "Weight"])
		hdr = self._table.horizontalHeader()
		hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
		hdr.setSectionResizeMode(1, QHeaderView.Stretch)
		hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
		hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
		root.addWidget(self._table)

		self._add.clicked.connect(self._on_add)
		self._del.clicked.connect(self._on_delete)
		self._filter.textChanged.connect(self._refresh)

		self._refresh()

	def _refresh(self) -> None:
		items = library_service.list_links()
		f = self._filter.text().strip().lower()
		self._table.setRowCount(0)
		for it in items:
			if f and (it.category or "").lower().find(f) < 0:
				continue
			row = self._table.rowCount(); self._table.insertRow(row)
			self._table.setItem(row, 0, QTableWidgetItem(str(it.id)))
			self._table.setItem(row, 1, QTableWidgetItem(it.url or ""))
			self._table.setItem(row, 2, QTableWidgetItem(it.category or ""))
			self._table.setItem(row, 3, QTableWidgetItem(str(it.weight)))

	def _on_add(self) -> None:
		url = self._url.text().strip()
		if not url:
			QMessageBox.warning(self, "Validation", "URL is required.")
			return
		category = self._category.text().strip() or None
		try:
			weight = int(self._weight.text().strip() or "1")
		except ValueError:
			QMessageBox.warning(self, "Validation", "Weight must be an integer.")
			return
		library_service.add_link(url=url, category=category, weight=weight)
		self._url.clear(); self._category.clear(); self._weight.clear(); self._refresh()

	def _on_delete(self) -> None:
		rows = self._table.selectionModel().selectedRows()
		if not rows:
			return
		for r in rows:
			id_item = self._table.item(r.row(), 0)
			if id_item:
				library_service.delete_link(int(id_item.text()))
		self._refresh()