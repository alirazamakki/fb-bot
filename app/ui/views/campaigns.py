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
	QTextEdit,
)

from app.core.config import AppConfig
from app.services import account_service, campaign_service, library_service


class CampaignBuilderView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config

		self._name = QLineEdit(); self._name.setPlaceholderText("Campaign name")
		self._create_btn = QPushButton("Create Campaign")
		self._preview_btn = QPushButton("Preview Tasks")

		# Multi-select lists
		self._accounts = QListWidget(); self._accounts.setSelectionMode(QListWidget.MultiSelection)
		self._posters = QListWidget(); self._posters.setSelectionMode(QListWidget.MultiSelection)
		self._captions = QListWidget(); self._captions.setSelectionMode(QListWidget.MultiSelection)
		self._links = QListWidget(); self._links.setSelectionMode(QListWidget.MultiSelection)

		# Filters
		self._filter_category = QLineEdit(); self._filter_category.setPlaceholderText("Category filter")
		self._filter_tag = QLineEdit(); self._filter_tag.setPlaceholderText("Tag filter substring")
		self._apply_filter = QPushButton("Apply Filters")

		# Options
		self._batch = QLineEdit(); self._batch.setPlaceholderText("Batch size (e.g., 2)")
		self._delay_min = QLineEdit(); self._delay_min.setPlaceholderText("Delay min (sec)")
		self._delay_max = QLineEdit(); self._delay_max.setPlaceholderText("Delay max (sec)")
		self._rotation = QComboBox(); self._rotation.addItems(["random", "round_robin", "per_account"]) 
		self._dry_run = QComboBox(); self._dry_run.addItems(["DRY_RUN", "REAL_POST"]) 
		self._retries = QLineEdit(); self._retries.setPlaceholderText("Retries (e.g., 2)")

		# Preview box
		self._preview = QTextEdit(); self._preview.setReadOnly(True)

		top = QHBoxLayout(); top.addWidget(self._name); top.addWidget(self._create_btn); top.addWidget(self._preview_btn)
		filters = QHBoxLayout(); filters.addWidget(self._filter_category); filters.addWidget(self._filter_tag); filters.addWidget(self._apply_filter)
		opts = QHBoxLayout();
		opts.addWidget(self._batch); opts.addWidget(self._delay_min); opts.addWidget(self._delay_max); opts.addWidget(self._rotation); opts.addWidget(self._dry_run); opts.addWidget(self._retries)

		root = QVBoxLayout(self)
		root.addLayout(top)
		root.addLayout(filters)
		root.addWidget(self._accounts)
		root.addWidget(self._posters)
		root.addWidget(self._captions)
		root.addWidget(self._links)
		root.addLayout(opts)
		root.addWidget(self._preview)

		self._create_btn.clicked.connect(self._on_create)
		self._preview_btn.clicked.connect(self._on_preview)
		self._apply_filter.clicked.connect(self._refresh_assets)
		self._refresh_all()

	def _refresh_all(self) -> None:
		self._accounts.clear()
		for acc in account_service.list_accounts():
			item = QListWidgetItem(f"A{acc.id} – {acc.name}"); item.setData(Qt.UserRole, ("account", acc.id))
			self._accounts.addItem(item)
		self._refresh_assets()

	def _match_filter(self, category: str | None, tags: object) -> bool:
		cat = (category or "").lower()
		tag_text = str(tags or "").lower()
		f_cat = self._filter_category.text().strip().lower()
		f_tag = self._filter_tag.text().strip().lower()
		return (f_cat in cat) and (f_tag in tag_text)

	def _refresh_assets(self) -> None:
		self._posters.clear()
		for p in library_service.list_posters():
			if self._match_filter(p.category, p.tags):
				item = QListWidgetItem(f"P{p.id} – {p.filename}"); item.setData(Qt.UserRole, ("poster", p.id))
				self._posters.addItem(item)
		self._captions.clear()
		for c in library_service.list_captions():
			if self._match_filter(c.category, c.tags):
				item = QListWidgetItem(f"C{c.id} – {c.text[:40]}"); item.setData(Qt.UserRole, ("caption", c.id))
				self._captions.addItem(item)
		self._links.clear()
		for l in library_service.list_links():
			if self._match_filter(l.category, None):
				item = QListWidgetItem(f"L{l.id} – {l.url[:60]}"); item.setData(Qt.UserRole, ("link", l.id))
				self._links.addItem(item)

	def _collect_ids(self, lw: QListWidget) -> list[int]:
		return [data[1] for data in (it.data(Qt.UserRole) for it in lw.selectedItems())]

	def _collect_config(self) -> tuple[dict, list[int]]:
		poster_ids = self._collect_ids(self._posters)
		caption_ids = self._collect_ids(self._captions)
		link_ids = self._collect_ids(self._links)
		try:
			batch = int(self._batch.text().strip() or "2")
			dmin = int(self._delay_min.text().strip() or "5")
			dmax = int(self._delay_max.text().strip() or "10")
			retries = int(self._retries.text().strip() or "2")
		except ValueError:
			raise ValueError("Batch/delay/retries must be integers")
		config = {
			"batch_size": batch,
			"delay_min": dmin,
			"delay_max": dmax,
			"rotation_mode": self._rotation.currentText(),
			"poster_ids": poster_ids,
			"caption_ids": caption_ids,
			"link_ids": link_ids,
			"dry_run": self._dry_run.currentText() == "DRY_RUN",
			"retries": retries,
		}
		account_ids = [data[1] for data in (it.data(Qt.UserRole) for it in self._accounts.selectedItems())]
		return config, account_ids

	def _on_preview(self) -> None:
		try:
			config, account_ids = self._collect_config()
		except ValueError as e:
			QMessageBox.warning(self, "Validation", str(e))
			return
		if not account_ids:
			QMessageBox.warning(self, "Validation", "Select at least one account.")
			return
		lines = []
		for acc_id in account_ids:
			acc = next((a for a in account_service.list_accounts() if a.id == acc_id), None)
			if not acc:
				continue
			groups = account_service.list_groups_for_account(acc_id)
			for g in groups:
				lines.append(f"Account {acc.name} -> Group {g.name} ({g.url})")
		self._preview.setText("\n".join(lines) or "No tasks (no groups)")

	def _on_create(self) -> None:
		name = self._name.text().strip()
		if not name:
			QMessageBox.warning(self, "Validation", "Campaign name is required.")
			return
		try:
			config, account_ids = self._collect_config()
		except ValueError as e:
			QMessageBox.warning(self, "Validation", str(e))
			return
		if not account_ids:
			QMessageBox.warning(self, "Validation", "Select at least one account.")
			return
		camp = campaign_service.create_campaign(name=name, config=config, account_ids=account_ids)
		QMessageBox.information(self, "Campaign Created", f"Created campaign #{camp.id} with tasks.")
		self._name.clear(); self._batch.clear(); self._delay_min.clear(); self._delay_max.clear(); self._retries.clear()