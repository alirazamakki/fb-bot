from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QComboBox

from app.core.config import AppConfig
from app.services.worker_service import WorkerService
from app.services import campaign_service


class WorkerThread(QThread):
	progress = Signal(str, dict)

	def __init__(self, campaign_id: int, batch_size: int) -> None:
		super().__init__()
		self._campaign_id = campaign_id
		self._batch_size = batch_size
		self.service = WorkerService(on_progress=lambda ev, p: self.progress.emit(ev, p))

	def run(self) -> None:
		self.service.run_campaign(self._campaign_id, self._batch_size)


class LiveConsoleView(QWidget):
	def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._config = config
		self._campaign_pick = QComboBox()
		self._campaign_id = QLineEdit(); self._campaign_id.setPlaceholderText("Campaign ID")
		self._batch_size = QLineEdit(); self._batch_size.setPlaceholderText("Batch size (e.g., 2)")
		self._run_btn = QPushButton("Run Campaign")
		self._stop_btn = QPushButton("Stop")
		self._log = QTextEdit(); self._log.setReadOnly(True)

		head = QHBoxLayout()
		head.addWidget(self._campaign_pick)
		head.addWidget(self._campaign_id)
		head.addWidget(self._batch_size)
		head.addWidget(self._run_btn)
		head.addWidget(self._stop_btn)

		root = QVBoxLayout(self)
		root.addLayout(head)
		root.addWidget(self._log)

		self._run_btn.clicked.connect(self._on_run)
		self._stop_btn.clicked.connect(self._on_stop)
		self._campaign_pick.currentIndexChanged.connect(self._on_pick_change)
		self._worker: WorkerThread | None = None

		self._refresh_campaigns()

	def _refresh_campaigns(self) -> None:
		self._campaign_pick.clear()
		for camp in campaign_service.list_campaigns():
			self._campaign_pick.addItem(f"#{camp.id} – {camp.name}", camp.id)

	def _on_pick_change(self) -> None:
		cid = self._campaign_pick.currentData()
		if cid:
			self._campaign_id.setText(str(cid))

	def _on_run(self) -> None:
		try:
			cid = int(self._campaign_id.text().strip())
		except ValueError:
			self._append("Invalid campaign id")
			return
		try:
			bs = int(self._batch_size.text().strip() or "2")
		except ValueError:
			self._append("Invalid batch size")
			return
		if self._worker and self._worker.isRunning():
			self._append("Worker already running")
			return
		self._worker = WorkerThread(campaign_id=cid, batch_size=bs)
		self._worker.progress.connect(self._on_progress)
		self._worker.finished.connect(lambda: self._append("All done."))
		self._worker.start()
		self._append(f"Started campaign {cid} with batch {bs}")

	def _on_stop(self) -> None:
		if self._worker and self._worker.isRunning():
			self._worker.service.cancel()
			self._append("Stop requested")

	def _on_progress(self, event: str, payload: dict) -> None:
		self._append(f"{event}: {payload}")

	def _append(self, msg: str) -> None:
		self._log.append(msg)