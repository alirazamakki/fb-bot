from __future__ import annotations

from typing import Callable, List, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem


class CommandPaletteDialog(QDialog):
	def __init__(self, actions: List[Tuple[str, Callable[[], None]]], parent=None) -> None:
		super().__init__(parent)
		self.setWindowTitle("Command Palette")
		self.resize(600, 400)
		self._all_actions = actions
		self._input = QLineEdit()
		self._input.setPlaceholderText("Type a command… (e.g., campaign, reload, accounts)")
		self._list = QListWidget()
		root = QVBoxLayout(self)
		root.addWidget(self._input)
		root.addWidget(self._list)
		self._input.textChanged.connect(self._on_change)
		self._list.itemActivated.connect(self._on_activate)
		self._refresh()

	def _refresh(self) -> None:
		self._list.clear()
		query = self._input.text().strip().lower()
		for title, _ in self._all_actions:
			if query and query not in title.lower():
				continue
			self._list.addItem(QListWidgetItem(title))
		if self._list.count() > 0:
			self._list.setCurrentRow(0)

	def _on_change(self, _text: str) -> None:
		self._refresh()

	def _on_activate(self, item: QListWidgetItem) -> None:
		title = item.text()
		for t, fn in self._all_actions:
			if t == title:
				fn()
				break
		self.accept()