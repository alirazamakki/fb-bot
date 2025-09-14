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


class CaptionLibraryView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config
		self._text = QLineEdit(); self._text.setPlaceholderText("Caption text (use {LINK}, {GROUP} etc.)")
		self._category = QLineEdit(); self._category.setPlaceholderText("Category (optional)")
		self._tags = QLineEdit(); self._tags.setPlaceholderText("Tags JSON (optional)")
		self._uniq = QLineEdit(); self._uniq.setPlaceholderText("Uniqueness mode: none/spin/append-random (optional)")
		self._add = QPushButton("Add Caption")
		self._del = QPushButton("Delete Selected")

		self._filter_cat = QLineEdit(); self._filter_cat.setPlaceholderText("Filter category")
		self._filter_tag = QLineEdit(); self._filter_tag.setPlaceholderText("Filter tag substring")

		head = QHBoxLayout();
		head.addWidget(self._text); head.addWidget(self._category); head.addWidget(self._tags); head.addWidget(self._uniq); head.addWidget(self._add); head.addWidget(self._del)

		filters = QHBoxLayout(); filters.addWidget(self._filter_cat); filters.addWidget(self._filter_tag)

		self._table = QTableWidget(0, 5)
		self._table.setHorizontalHeaderLabels(["ID", "Text", "Category", "Tags", "Uniqueness"])
		hdr = self._table.horizontalHeader()
		hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
		hdr.setSectionResizeMode(1, QHeaderView.Stretch)
		hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
		hdr.setSectionResizeMode(3, QHeaderView.Stretch)
		hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)

		root = QVBoxLayout(self)
		root.addLayout(filters)
		root.addLayout(head)
		root.addWidget(self._table)

		self._add.clicked.connect(self._on_add)
		self._del.clicked.connect(self._on_delete)
		self._filter_cat.textChanged.connect(self._refresh)
		self._filter_tag.textChanged.connect(self._refresh)

		self._refresh()

	def _matches(self, cat: str | None, tags: object) -> bool:
		c = (cat or "").lower(); t = str(tags or "").lower()
		fc = self._filter_cat.text().strip().lower(); ft = self._filter_tag.text().strip().lower()
		return (fc in c) and (ft in t)

	def _refresh(self) -> None:
		items = library_service.list_captions()
		self._table.setRowCount(0)
		for it in items:
			if not self._matches(it.category, it.tags):
				continue
			row = self._table.rowCount(); self._table.insertRow(row)
			self._table.setItem(row, 0, QTableWidgetItem(str(it.id)))
			self._table.setItem(row, 1, QTableWidgetItem(it.text or ""))
			self._table.setItem(row, 2, QTableWidgetItem(it.category or ""))
			self._table.setItem(row, 3, QTableWidgetItem(str(it.tags) if it.tags else ""))
			self._table.setItem(row, 4, QTableWidgetItem(it.uniqueness_mode or ""))

	def _on_add(self) -> None:
		text = self._text.text().strip()
		if not text:
			QMessageBox.warning(self, "Validation", "Caption text is required.")
			return
		category = self._category.text().strip() or None
		tags = self._tags.text().strip() or None
		uniq = self._uniq.text().strip() or None
		library_service.add_caption(text=text, category=category, tags_json=tags, uniqueness_mode=uniq)
		self._text.clear(); self._category.clear(); self._tags.clear(); self._uniq.clear(); self._refresh()

	def _on_delete(self) -> None:
		rows = self._table.selectionModel().selectedRows()
		if not rows:
			return
		for r in rows:
			id_item = self._table.item(r.row(), 0)
			if id_item:
				library_service.delete_caption(int(id_item.text()))
		self._refresh()