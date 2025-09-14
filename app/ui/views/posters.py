from __future__ import annotations

from PySide6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QHBoxLayout,
	QLineEdit,
	QPushButton,
	QFileDialog,
	QMessageBox,
	QLabel,
	QScrollArea,
)
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PySide6.QtCore import Qt

from app.core.config import AppConfig
from app.services import library_service


class PosterLibraryView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config
		self.setAcceptDrops(True)
		self._path = QLineEdit(); self._path.setPlaceholderText("Image file path")
		self._browse = QPushButton("Browse…")
		self._category = QLineEdit(); self._category.setPlaceholderText("Category (optional)")
		self._tags = QLineEdit(); self._tags.setPlaceholderText("Tags JSON (optional)")
		self._add = QPushButton("Add Poster")
		self._filter = QLineEdit(); self._filter.setPlaceholderText("Filter by category")

		head = QHBoxLayout()
		head.addWidget(self._path)
		head.addWidget(self._browse)
		head.addWidget(self._category)
		head.addWidget(self._tags)
		head.addWidget(self._add)

		root = QVBoxLayout(self)
		root.addLayout(head)
		root.addWidget(self._filter)

		# Grid area
		self._scroll = QScrollArea(); self._scroll.setWidgetResizable(True)
		self._grid_host = QWidget(); self._grid_layout = QVBoxLayout(self._grid_host)
		self._grid_layout.setAlignment(Qt.AlignTop)
		self._scroll.setWidget(self._grid_host)
		root.addWidget(self._scroll)

		self._browse.clicked.connect(self._on_browse)
		self._add.clicked.connect(self._on_add)
		self._filter.textChanged.connect(self._refresh)

		self._refresh()

	def dragEnterEvent(self, event: QDragEnterEvent) -> None:
		if event.mimeData().hasUrls():
			event.acceptProposedAction()

	def dropEvent(self, event: QDropEvent) -> None:
		for url in event.mimeData().urls():
			path = url.toLocalFile()
			if not path:
				continue
			try:
				library_service.add_poster(path)
			except Exception:
				pass
		self._refresh()

	def _refresh(self) -> None:
		# clear grid
		while self._grid_layout.count():
			child = self._grid_layout.takeAt(0)
			if child and child.widget():
				child.widget().deleteLater()
		items = library_service.list_posters()
		f = self._filter.text().strip().lower()
		cols = max(1, int(self._config.poster_grid_cols))
		row_container = None
		row_layout = None
		col_count = 0
		for it in items:
			if f and (it.category or "").lower().find(f) < 0:
				continue
			if row_layout is None or col_count >= cols:
				row_container = QWidget(); row_layout = QHBoxLayout(row_container)
				row_layout.setAlignment(Qt.AlignLeft)
				self._grid_layout.addWidget(row_container)
				col_count = 0

			card = self._make_card(it.id, it.filepath, it.filename, it.category, it.tags)
			row_layout.addWidget(card)
			col_count += 1

		# spacer
		sp = QWidget(); sp.setMinimumHeight(1)
		self._grid_layout.addWidget(sp)

	def _make_card(self, pid: int, path: str, filename: str | None, category: str | None, tags: object) -> QWidget:
		w = QWidget(); lay = QVBoxLayout(w)
		img = QLabel()
		try:
			pix = QPixmap(path)
			if not pix.isNull():
				img.setPixmap(pix.scaledToHeight(120))
		except Exception:
			pass
		title = QLabel((filename or "")[:60])
		meta = QLabel((category or "") + ("\n" + str(tags) if tags else ""))
		btns = QHBoxLayout()
		del_btn = QPushButton("Delete")
		del_btn.clicked.connect(lambda: self._on_delete(pid))
		btns.addWidget(del_btn)
		lay.addWidget(img); lay.addWidget(title); lay.addWidget(meta); lay.addLayout(btns)
		return w

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

	def _on_delete(self, pid: int) -> None:
		try:
			library_service.delete_poster(pid)
		except Exception:
			pass
		self._refresh()