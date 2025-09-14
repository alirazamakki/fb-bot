from __future__ import annotations

from typing import List, Set

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
	QDialog,
	QVBoxLayout,
	QHBoxLayout,
	QLineEdit,
	QLabel,
	QPushButton,
	QScrollArea,
	QWidget,
	QGridLayout,
	QCheckBox,
)

from app.services import library_service


class _GridDialog(QDialog):
	def __init__(self, title: str, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.setWindowTitle(title)
		self.resize(800, 600)
		self._filter_cat = QLineEdit(); self._filter_cat.setPlaceholderText("Filter category")
		self._filter_tag = QLineEdit(); self._filter_tag.setPlaceholderText("Filter tags (substring)")
		self._apply = QPushButton("Apply")
		self._use = QPushButton("Use Selected")

		head = QHBoxLayout(); head.addWidget(self._filter_cat); head.addWidget(self._filter_tag); head.addWidget(self._apply); head.addWidget(self._use)

		self._scroll = QScrollArea(); self._scroll.setWidgetResizable(True)
		self._grid_host = QWidget()
		self._grid = QGridLayout(self._grid_host)
		self._grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		self._scroll.setWidget(self._grid_host)

		root = QVBoxLayout(self)
		root.addLayout(head)
		root.addWidget(self._scroll)

		self._apply.clicked.connect(self._refresh)

	def _match(self, cat: str | None, tags: object) -> bool:
		c = (cat or "").lower(); t = str(tags or "").lower()
		fc = self._filter_cat.text().strip().lower(); ft = self._filter_tag.text().strip().lower()
		return (fc in c) and (ft in t)

	def _refresh(self) -> None:
		raise NotImplementedError


class PosterSelectorDialog(_GridDialog):
	def __init__(self, preselected: List[int] | None = None, parent: QWidget | None = None) -> None:
		super().__init__("Select Posters", parent)
		self.selected_ids: Set[int] = set(preselected or [])
		self._refresh()
		self._use.clicked.connect(self.accept)

	def _refresh(self) -> None:
		# clear grid
		while self._grid.count():
			child = self._grid.takeAt(0)
			if child and child.widget():
				child.widget().deleteLater()
		items = library_service.list_posters()
		row, col = 0, 0
		for it in items:
			if not self._match(it.category, it.tags):
				continue
			container = QWidget(); lay = QVBoxLayout(container)
			cb = QCheckBox(f"#{it.id} {it.filename}")
			cb.setChecked(it.id in self.selected_ids)
			cb.stateChanged.connect(lambda state, pid=it.id: self._toggle(pid, state))
			img = QLabel()
			try:
				pix = QPixmap(it.filepath)
				if not pix.isNull():
					img.setPixmap(pix.scaledToHeight(96))
			except Exception:
				pass
			meta = QLabel((it.category or "") + ("\n" + str(it.tags) if it.tags else ""))
			lay.addWidget(img); lay.addWidget(cb); lay.addWidget(meta)
			self._grid.addWidget(container, row, col)
			col += 1
			if col >= 3:
				col = 0; row += 1

	def _toggle(self, pid: int, state: int) -> None:
		if state == Qt.Checked:
			self.selected_ids.add(pid)
		else:
			self.selected_ids.discard(pid)


class CaptionSelectorDialog(_GridDialog):
	def __init__(self, preselected: List[int] | None = None, parent: QWidget | None = None) -> None:
		super().__init__("Select Captions", parent)
		self.selected_ids: Set[int] = set(preselected or [])
		self._refresh()
		self._use.clicked.connect(self.accept)

	def _refresh(self) -> None:
		while self._grid.count():
			child = self._grid.takeAt(0)
			if child and child.widget():
				child.widget().deleteLater()
		items = library_service.list_captions()
		row, col = 0, 0
		for it in items:
			if not self._match(it.category, it.tags):
				continue
			container = QWidget(); lay = QVBoxLayout(container)
			cb = QCheckBox(f"#{it.id} {it.category or ''}")
			cb.setChecked(it.id in self.selected_ids)
			cb.stateChanged.connect(lambda state, cid=it.id: self._toggle(cid, state))
			text = QLabel((it.text or "")[:180])
			text.setWordWrap(True)
			meta = QLabel(str(it.tags) if it.tags else "")
			lay.addWidget(cb); lay.addWidget(text); lay.addWidget(meta)
			self._grid.addWidget(container, row, col)
			col += 1
			if col >= 2:
				col = 0; row += 1

	def _toggle(self, cid: int, state: int) -> None:
		if state == Qt.Checked:
			self.selected_ids.add(cid)
		else:
			self.selected_ids.discard(cid)


class LinkSelectorDialog(_GridDialog):
	def __init__(self, preselected: List[int] | None = None, parent: QWidget | None = None) -> None:
		super().__init__("Select Links", parent)
		self.selected_ids: Set[int] = set(preselected or [])
		self._refresh()
		self._use.clicked.connect(self.accept)

	def _refresh(self) -> None:
		while self._grid.count():
			child = self._grid.takeAt(0)
			if child and child.widget():
				child.widget().deleteLater()
		items = library_service.list_links()
		row, col = 0, 0
		for it in items:
			# For links we only filter by category
			if not self._match(it.category, None):
				continue
			container = QWidget(); lay = QVBoxLayout(container)
			cb = QCheckBox(f"#{it.id} weight={it.weight}")
			cb.setChecked(it.id in self.selected_ids)
			cb.stateChanged.connect(lambda state, lid=it.id: self._toggle(lid, state))
			url = QLabel((it.url or "")[:120])
			url.setWordWrap(True)
			meta = QLabel(it.category or "")
			lay.addWidget(cb); lay.addWidget(url); lay.addWidget(meta)
			self._grid.addWidget(container, row, col)
			col += 1
			if col >= 2:
				col = 0; row += 1

	def _toggle(self, lid: int, state: int) -> None:
		if state == Qt.Checked:
			self.selected_ids.add(lid)
		else:
			self.selected_ids.discard(lid)