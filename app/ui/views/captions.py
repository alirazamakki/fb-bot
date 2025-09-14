from __future__ import annotations

from PySide6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QHBoxLayout,
	QLineEdit,
	QPushButton,
	QLabel,
	QScrollArea,
	QMessageBox,
)
from PySide6.QtCore import Qt

from app.core.config import AppConfig
from app.services import library_service


class CaptionLibraryView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config
		# Compose/test input
		self._compose = QLineEdit(); self._compose.setPlaceholderText("Compose caption here (use {LINK}, {GROUP})")
		self._category = QLineEdit(); self._category.setPlaceholderText("Category (optional)")
		self._tags = QLineEdit(); self._tags.setPlaceholderText("Tags JSON (optional)")
		self._uniq = QLineEdit(); self._uniq.setPlaceholderText("Uniqueness mode (optional)")
		self._add = QPushButton("Add Caption")

		self._filter_cat = QLineEdit(); self._filter_cat.setPlaceholderText("Filter category")
		self._filter_tag = QLineEdit(); self._filter_tag.setPlaceholderText("Filter tag substring")

		head = QHBoxLayout();
		head.addWidget(self._compose); head.addWidget(self._category); head.addWidget(self._tags); head.addWidget(self._uniq); head.addWidget(self._add)

		filters = QHBoxLayout(); filters.addWidget(self._filter_cat); filters.addWidget(self._filter_tag)

		root = QVBoxLayout(self)
		root.addLayout(head)
		root.addLayout(filters)

		self._scroll = QScrollArea(); self._scroll.setWidgetResizable(True)
		self._grid_host = QWidget(); self._grid_layout = QVBoxLayout(self._grid_host)
		self._grid_layout.setAlignment(Qt.AlignTop)
		self._scroll.setWidget(self._grid_host)
		root.addWidget(self._scroll)

		self._add.clicked.connect(self._on_add)
		self._filter_cat.textChanged.connect(self._refresh)
		self._filter_tag.textChanged.connect(self._refresh)

		self._refresh()

	def _matches(self, cat: str | None, tags: object) -> bool:
		c = (cat or "").lower(); t = str(tags or "").lower()
		fc = self._filter_cat.text().strip().lower(); ft = self._filter_tag.text().strip().lower()
		return (fc in c) and (ft in t)

	def _refresh(self) -> None:
		while self._grid_layout.count():
			child = self._grid_layout.takeAt(0)
			if child and child.widget():
				child.widget().deleteLater()
		items = library_service.list_captions()
		row_container = None
		row_layout = None
		col_count = 0
		cols = max(1, int(self._config.caption_grid_cols))
		for it in items:
			if not self._matches(it.category, it.tags):
				continue
			if row_layout is None or col_count >= cols:
				row_container = QWidget(); row_layout = QHBoxLayout(row_container)
				row_layout.setAlignment(Qt.AlignLeft)
				self._grid_layout.addWidget(row_container)
				col_count = 0

			card = self._make_card(it.id, it.text, it.category, it.tags, it.uniqueness_mode)
			row_layout.addWidget(card)
			col_count += 1
		# spacer
		sp = QWidget(); sp.setMinimumHeight(1)
		self._grid_layout.addWidget(sp)

	def _make_card(self, cid: int, text: str | None, cat: str | None, tags: object, uniq: str | None) -> QWidget:
		w = QWidget(); lay = QVBoxLayout(w)
		lbl = QLabel((text or "")[:240]); lbl.setWordWrap(True)
		meta = QLabel((cat or "") + ("\n" + str(tags) if tags else "") + (f"\n{uniq}" if uniq else ""))
		btns = QHBoxLayout()
		del_btn = QPushButton("Delete")
		del_btn.clicked.connect(lambda: self._on_delete(cid))
		btns.addWidget(del_btn)
		lay.addWidget(lbl); lay.addWidget(meta); lay.addLayout(btns)
		return w

	def _on_add(self) -> None:
		text = self._compose.text().strip()
		if not text:
			QMessageBox.warning(self, "Validation", "Caption text is required.")
			return
		category = self._category.text().strip() or None
		tags = self._tags.text().strip() or None
		uniq = self._uniq.text().strip() or None
		library_service.add_caption(text=text, category=category, tags_json=tags, uniqueness_mode=uniq)
		self._compose.clear(); self._category.clear(); self._tags.clear(); self._uniq.clear(); self._refresh()

	def _on_delete(self, cid: int) -> None:
		try:
			library_service.delete_caption(cid)
		except Exception:
			pass
		self._refresh()