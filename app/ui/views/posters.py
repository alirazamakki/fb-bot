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
	QFileDialog,
	QMessageBox,
	QLabel,
)
from PySide6.QtGui import QPixmap

from app.core.config import AppConfig
from app.services import library_service


class PosterLibraryView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config
		self._path = QLineEdit(); self._path.setPlaceholderText("Image file path")
		self._browse = QPushButton("Browse…")
		self._category = QLineEdit(); self._category.setPlaceholderText("Category (optional)")
		self._tags = QLineEdit(); self._tags.setPlaceholderText("Tags JSON (optional)")
		self._add = QPushButton("Add Poster")
		self._del = QPushButton("Delete Selected")
		self._filter = QLineEdit(); self._filter.setPlaceholderText("Filter by category")

		head = QHBoxLayout()
		head.addWidget(self._path)
		head.addWidget(self._browse)
		head.addWidget(self._category)
		head.addWidget(self._tags)
		head.addWidget(self._add)
		head.addWidget(self._del)

		root = QVBoxLayout(self)
		root.addLayout(head)
		root.addWidget(self._filter)

		self._table = QTableWidget(0, 6)
		self._table.setHorizontalHeaderLabels(["ID", "Thumb", "Filename", "Path", "Category", "Tags"])
		hdr = self._table.horizontalHeader()
		hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
		hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
		hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
		hdr.setSectionResizeMode(3, QHeaderView.Stretch)
		hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
		hdr.setSectionResizeMode(5, QHeaderView.Stretch)
		root.addWidget(self._table)

		self._browse.clicked.connect(self._on_browse)
		self._add.clicked.connect(self._on_add)
		self._del.clicked.connect(self._on_delete)
		self._filter.textChanged.connect(self._refresh)

		self._refresh()

	def _refresh(self) -> None:
		items = library_service.list_posters()
		f = self._filter.text().strip().lower()
		self._table.setRowCount(0)
		for it in items:
			if f and (it.category or "").lower().find(f) < 0:
				continue
			row = self._table.rowCount()
			self._table.insertRow(row)
			self._table.setItem(row, 0, QTableWidgetItem(str(it.id)))
			# thumb
			lbl = QLabel()
			try:
				pix = QPixmap(it.filepath)
				if not pix.isNull():
					self._set_thumb(lbl, pix)
			except Exception:
				pass
			self._table.setCellWidget(row, 1, lbl)
			self._table.setItem(row, 2, QTableWidgetItem(it.filename or ""))
			self._table.setItem(row, 3, QTableWidgetItem(it.filepath or ""))
			self._table.setItem(row, 4, QTableWidgetItem(it.category or ""))
			self._table.setItem(row, 5, QTableWidgetItem(str(it.tags) if it.tags else ""))

	def _set_thumb(self, lbl: QLabel, pix: QPixmap) -> None:
		scaled = pix.scaledToHeight(64)
		lbl.setPixmap(scaled)

	def _on_browse(self) -> None:
		path, _ = QFileDialog.getOpenFileName(self, "Select image", "", "Images (*.png *.jpg *.jpeg *.webp *.gif);;All files (*.*)")
		if path:
			self._path.setText(path)

	def _on_add(self) -> None:
		path = self._path.text().strip()
		if not path:
			QMessageBox.warning(self, "Validation", "Choose an image file.")
			return
		category = self._category.text().strip() or None
		tags = self._tags.text().strip() or None
		try:
			library_service.add_poster(path, category=category, tags_json=tags)
		except Exception as exc:  # noqa: BLE001
			QMessageBox.critical(self, "Error", str(exc))
			return
		self._path.clear(); self._category.clear(); self._tags.clear()
		self._refresh()

	def _on_delete(self) -> None:
		rows = self._table.selectionModel().selectedRows()
		if not rows:
			return
		for r in rows:
			id_item = self._table.item(r.row(), 0)
			if id_item:
				library_service.delete_poster(int(id_item.text()))
		self._refresh()