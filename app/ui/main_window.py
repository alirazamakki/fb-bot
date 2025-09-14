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
)

from app.core.config import AppConfig
from app.ui.views.dashboard import DashboardView
from app.ui.views.accounts import AccountManagerView
from app.ui.views.groups import GroupManagerView
from app.ui.views.posters import PosterLibraryView
from app.ui.views.captions import CaptionLibraryView
from app.ui.views.links import LinkManagerView
from app.ui.views.campaigns import CampaignBuilderView
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

		self._nav_list = QListWidget()
		self._nav_list.setAlternatingRowColors(True)
		self._nav_list.setSelectionMode(QListWidget.SingleSelection)
		self._nav_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
		self._nav_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self._nav_list.setFixedWidth(220)

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
			("scheduler", "Scheduler", SchedulerView(config)),
			("console", "Live Console", LiveConsoleView(config)),
			("logs", "Logs & Reports", LogsView(config)),
			("settings", "Settings", SettingsView(config)),
		]

		self._sections: Dict[str, Section] = {}
		for key, title, widget in sections:
			self._add_section(key, title, widget)

		# Layout: left nav + right stacked
		container = QWidget()
		layout = QHBoxLayout(container)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self._nav_list)
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