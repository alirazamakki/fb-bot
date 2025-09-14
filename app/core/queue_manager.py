from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional

from loguru import logger


@dataclass
class WorkerTask:
	account_id: int
	payload: dict


class PoolManager:
	"""Fixed-size worker pool that keeps N concurrent workers until queue drains."""

	def __init__(self, batch_size: int) -> None:
		self._batch_size = batch_size
		self._queue: queue.Queue[WorkerTask] = queue.Queue()
		self._threads: List[threading.Thread] = []
		self._stop = threading.Event()

	def submit_tasks(self, tasks: Iterable[WorkerTask]) -> None:
		for t in tasks:
			self._queue.put(t)

	def run(self, worker_fn: Callable[[WorkerTask], None]) -> None:
		self._stop.clear()
		self._threads = []
		for i in range(self._batch_size):
			thr = threading.Thread(target=self._worker_loop, args=(worker_fn, i + 1), daemon=True)
			thr.start()
			self._threads.append(thr)

		self._queue.join()
		self._stop.set()
		for thr in self._threads:
			thr.join()

	def _worker_loop(self, worker_fn: Callable[[WorkerTask], None], worker_id: int) -> None:
		while not self._stop.is_set():
			try:
				task = self._queue.get_nowait()
			except queue.Empty:
				break
			try:
				logger.info(f"Worker {worker_id} starting account {task.account_id}")
				worker_fn(task)
				logger.info(f"Worker {worker_id} finished account {task.account_id}")
			except Exception as exc:  # noqa: BLE001
				logger.exception(f"Worker {worker_id} error on account {task.account_id}: {exc}")
			finally:
				self._queue.task_done()