from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
	QMainWindow,
	QWidget,
	QListWidget,
	QListWidgetItem,
	QStackedWidget,
	QHBoxLayout,
	QVBoxLayout,
	QPushButton,
	QMessageBox,
)

from pathlib import Path

from app.core.config import AppConfig
from app.ui.views.dashboard import DashboardView
from app.ui.views.accounts import AccountManagerView
from app.ui.views.groups import GroupManagerView
from app.ui.views.posters import PosterLibraryView
from app.ui.views.captions import CaptionLibraryView
from app.ui.views.links import LinkManagerView
from app.ui.views.campaigns import CampaignBuilderView
from app.ui.views.campaigns_list import CampaignsListView
from app.ui.views.scheduler import SchedulerView
from app.ui.views.console import LiveConsoleView
from app.ui.views.logs import LogsView
from app.ui.views.settings import SettingsView


@dataclass(frozen=True)
class Section:
	key: str
	title: str
	widget: QWidget


class MainWindow(QMainWindow):
	"""Main application window with left navigation and stacked views."""

	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config
		self.setWindowTitle("FB Group Campaign Manager")
		self.resize(1200, 800)

		# Left navigation list
		self._nav_list = QListWidget()
		self._nav_list.setAlternatingRowColors(True)
		self._nav_list.setSelectionMode(QListWidget.SingleSelection)
		self._nav_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
		self._nav_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self._nav_list.setFixedWidth(240)

		# Sticky controls under the nav
		self._btn_refresh = QPushButton("Refresh")
		self._btn_clear_cache = QPushButton("Clear Cache")
		self._btn_refresh.clicked.connect(self._on_global_refresh)
		self._btn_clear_cache.clicked.connect(self._on_clear_cache)

		# Sidebar container (nav + sticky buttons)
		sidebar = QWidget()
		vbox = QVBoxLayout(sidebar)
		vbox.setContentsMargins(0, 0, 0, 0)
		vbox.addWidget(self._nav_list, 1)
		vbox.addWidget(self._btn_refresh, 0)
		vbox.addWidget(self._btn_clear_cache, 0)

		self._stack = QStackedWidget()

		# Build sections
		sections: List[Tuple[str, str, QWidget]] = [
			("dashboard", "Dashboard", DashboardView(config)),
			("accounts", "Account Manager", AccountManagerView(config)),
			("groups", "Group Manager", GroupManagerView(config)),
			("posters", "Poster Library", PosterLibraryView(config)),
			("captions", "Caption Library", CaptionLibraryView(config)),
			("links", "Link Manager", LinkManagerView(config)),
			("campaigns", "Campaign Builder", CampaignBuilderView(config)),
			("campaigns_list", "Campaigns", CampaignsListView(config)),
			("scheduler", "Scheduler", SchedulerView(config)),
			("console", "Live Console", LiveConsoleView(config)),
			("logs", "Logs & Reports", LogsView(config)),
			("settings", "Settings", SettingsView(config)),
		]

		self._sections: Dict[str, Section] = {}
		for key, title, widget in sections:
			self._add_section(key, title, widget)

		# Layout: sidebar + right stacked
		container = QWidget()
		layout = QHBoxLayout(container)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(sidebar)
		layout.addWidget(self._stack)
		self.setCentralWidget(container)

		self._nav_list.currentRowChanged.connect(self._stack.setCurrentIndex)
		self._nav_list.setCurrentRow(0)

	def _add_section(self, key: str, title: str, widget: QWidget) -> None:
		section = Section(key=key, title=title, widget=widget)
		self._sections[key] = section
		item = QListWidgetItem(title)
		self._nav_list.addItem(item)
		self._stack.addWidget(widget)

	def _on_global_refresh(self) -> None:
		# Best-effort refresh of current view
		w = self._stack.currentWidget()
		for method_name in ("_refresh", "refresh", "_refresh_campaigns"):
			if hasattr(w, method_name):
				try:
					getattr(w, method_name)()
				except Exception:
					pass

	def _on_clear_cache(self) -> None:
		# Clear debug artifacts in logs (keep main log file)
		logs_dir = Path(self._config.logs_dir)
		deleted = 0
		if logs_dir.exists():
			for p in logs_dir.glob("fb_debug_*.png"):
				try:
					p.unlink()
					deleted += 1
				except Exception:
					pass
			for p in logs_dir.glob("fb_debug_*.html"):
				try:
					p.unlink()
					deleted += 1
				except Exception:
					pass
		QMessageBox.information(self, "Clear Cache", f"Deleted {deleted} debug artifact(s).")