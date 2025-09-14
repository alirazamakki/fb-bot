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
from app.services import account_service, campaign_service
from app.ui.views.selectors import PosterSelectorDialog, CaptionSelectorDialog, LinkSelectorDialog


class CampaignBuilderView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config

		self._name = QLineEdit(); self._name.setPlaceholderText("Campaign name")
		self._create_btn = QPushButton("Create Campaign")
		self._preview_btn = QPushButton("Preview Tasks")

		# Accounts selection remains as list
		self._accounts = QListWidget(); self._accounts.setSelectionMode(QListWidget.MultiSelection)

		# Buttons to open grid selectors
		self._pick_posters = QPushButton("Select Posters…")
		self._pick_captions = QPushButton("Select Captions…")
		self._pick_links = QPushButton("Select Links…")
		self._pick_posters.clicked.connect(self._on_pick_posters)
		self._pick_captions.clicked.connect(self._on_pick_captions)
		self._pick_links.clicked.connect(self._on_pick_links)
		self._poster_ids: list[int] = []
		self._caption_ids: list[int] = []
		self._link_ids: list[int] = []

		# Options (batch size removed; controlled globally in Settings/Console)
		self._delay_min = QLineEdit(); self._delay_min.setPlaceholderText("Delay min (sec)")
		self._delay_max = QLineEdit(); self._delay_max.setPlaceholderText("Delay max (sec)")
		self._rotation = QComboBox(); self._rotation.addItems(["random", "round_robin", "per_account"]) 
		self._dry_run = QComboBox(); self._dry_run.addItems(["DRY_RUN", "REAL_POST"]) 
		self._retries = QLineEdit(); self._retries.setPlaceholderText("Retries (e.g., 2)")

		# Preview box
		self._preview = QTextEdit(); self._preview.setReadOnly(True)

		top = QHBoxLayout(); top.addWidget(self._name); top.addWidget(self._create_btn); top.addWidget(self._preview_btn)
		pick = QHBoxLayout(); pick.addWidget(self._pick_posters); pick.addWidget(self._pick_captions); pick.addWidget(self._pick_links)
		opts = QHBoxLayout(); opts.addWidget(self._delay_min); opts.addWidget(self._delay_max); opts.addWidget(self._rotation); opts.addWidget(self._dry_run); opts.addWidget(self._retries)

		root = QVBoxLayout(self)
		root.addLayout(top)
		root.addWidget(self._accounts)
		root.addLayout(pick)
		root.addLayout(opts)
		root.addWidget(self._preview)

		self._create_btn.clicked.connect(self._on_create)
		self._preview_btn.clicked.connect(self._on_preview)
		self._refresh_accounts()

	def _refresh_accounts(self) -> None:
		self._accounts.clear()
		for acc in account_service.list_accounts():
			item = QListWidgetItem(f"A{acc.id} – {acc.name}"); item.setData(Qt.UserRole, ("account", acc.id))
			self._accounts.addItem(item)

	def _on_pick_posters(self) -> None:
		dlg = PosterSelectorDialog(preselected=self._poster_ids, parent=self)
		if dlg.exec():
			self._poster_ids = sorted(dlg.selected_ids)

	def _on_pick_captions(self) -> None:
		dlg = CaptionSelectorDialog(preselected=self._caption_ids, parent=self)
		if dlg.exec():
			self._caption_ids = sorted(dlg.selected_ids)

	def _on_pick_links(self) -> None:
		dlg = LinkSelectorDialog(preselected=self._link_ids, parent=self)
		if dlg.exec():
			self._link_ids = sorted(dlg.selected_ids)

	def _collect_config(self) -> tuple[dict, list[int]]:
		try:
			dmin = int(self._delay_min.text().strip() or "5")
			dmax = int(self._delay_max.text().strip() or "10")
			retries = int(self._retries.text().strip() or "2")
		except ValueError:
			raise ValueError("Delay/retries must be integers")
		config = {
			"delay_min": dmin,
			"delay_max": dmax,
			"rotation_mode": self._rotation.currentText(),
			"poster_ids": self._poster_ids,
			"caption_ids": self._caption_ids,
			"link_ids": self._link_ids,
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
			from app.services import account_service as _as
			groups = _as.list_groups_for_account(acc_id)
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
		self._name.clear(); self._delay_min.clear(); self._delay_max.clear(); self._retries.clear()