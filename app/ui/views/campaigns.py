from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QHBoxLayout,
	QLineEdit,
	QPushButton,
	QListWidget,
	QListWidgetItem,
	QMessageBox,
	QComboBox,
)

from app.core.config import AppConfig
from app.services import account_service, campaign_service, library_service


class CampaignBuilderView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config

		self._name = QLineEdit()
		self._name.setPlaceholderText("Campaign name")
		self._create_btn = QPushButton("Create Campaign")

		# Multi-select lists
		self._accounts = QListWidget(); self._accounts.setSelectionMode(QListWidget.MultiSelection)
		self._posters = QListWidget(); self._posters.setSelectionMode(QListWidget.MultiSelection)
		self._captions = QListWidget(); self._captions.setSelectionMode(QListWidget.MultiSelection)
		self._links = QListWidget(); self._links.setSelectionMode(QListWidget.MultiSelection)

		# Options
		self._batch = QLineEdit(); self._batch.setPlaceholderText("Batch size (e.g., 2)")
		self._delay_min = QLineEdit(); self._delay_min.setPlaceholderText("Delay min (sec)")
		self._delay_max = QLineEdit(); self._delay_max.setPlaceholderText("Delay max (sec)")
		self._rotation = QComboBox(); self._rotation.addItems(["random", "round_robin", "per_account"]) 

		top = QHBoxLayout(); top.addWidget(self._name); top.addWidget(self._create_btn)
		opts = QHBoxLayout();
		opts.addWidget(self._batch); opts.addWidget(self._delay_min); opts.addWidget(self._delay_max); opts.addWidget(self._rotation)

		root = QVBoxLayout(self)
		root.addLayout(top)
		root.addWidget(self._accounts)
		root.addWidget(self._posters)
		root.addWidget(self._captions)
		root.addWidget(self._links)
		root.addLayout(opts)

		self._create_btn.clicked.connect(self._on_create)
		self._refresh_all()

	def _refresh_all(self) -> None:
		self._accounts.clear()
		for acc in account_service.list_accounts():
			item = QListWidgetItem(f"A{acc.id} – {acc.name}"); item.setData(Qt.UserRole, ("account", acc.id))
			self._accounts.addItem(item)
		self._posters.clear()
		for p in library_service.list_posters():
			item = QListWidgetItem(f"P{p.id} – {p.filename}"); item.setData(Qt.UserRole, ("poster", p.id))
			self._posters.addItem(item)
		self._captions.clear()
		for c in library_service.list_captions():
			item = QListWidgetItem(f"C{c.id} – {c.text[:40]}"); item.setData(Qt.UserRole, ("caption", c.id))
			self._captions.addItem(item)
		self._links.clear()
		for l in library_service.list_links():
			item = QListWidgetItem(f"L{l.id} – {l.url[:60]}"); item.setData(Qt.UserRole, ("link", l.id))
			self._links.addItem(item)

	def _on_create(self) -> None:
		name = self._name.text().strip()
		if not name:
			QMessageBox.warning(self, "Validation", "Campaign name is required.")
			return
		account_ids = [data[1] for data in (it.data(Qt.UserRole) for it in self._accounts.selectedItems())]
		if not account_ids:
			QMessageBox.warning(self, "Validation", "Select at least one account.")
			return
		poster_ids = [data[1] for data in (it.data(Qt.UserRole) for it in self._posters.selectedItems())]
		caption_ids = [data[1] for data in (it.data(Qt.UserRole) for it in self._captions.selectedItems())]
		link_ids = [data[1] for data in (it.data(Qt.UserRole) for it in self._links.selectedItems())]
		try:
			batch = int(self._batch.text().strip() or "2")
			dmin = int(self._delay_min.text().strip() or "5")
			dmax = int(self._delay_max.text().strip() or "10")
		except ValueError:
			QMessageBox.warning(self, "Validation", "Batch and delays must be integers.")
			return
		config = {
			"batch_size": batch,
			"delay_min": dmin,
			"delay_max": dmax,
			"rotation_mode": self._rotation.currentText(),
			"poster_ids": poster_ids,
			"caption_ids": caption_ids,
			"link_ids": link_ids,
		}
		camp = campaign_service.create_campaign(name=name, config=config, account_ids=account_ids)
		QMessageBox.information(self, "Campaign Created", f"Created campaign #{camp.id} with tasks.")
		self._name.clear()
		self._batch.clear(); self._delay_min.clear(); self._delay_max.clear()