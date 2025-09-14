from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from loguru import logger


@dataclass
class AccountJob:
    account_id: int


def profile_worker(task_queue: queue.Queue, worker_id: int, stop_event: threading.Event, job_fn: Callable[[int], None]) -> None:
    while not stop_event.is_set():
        try:
            job: AccountJob = task_queue.get_nowait()
        except queue.Empty:
            break

        try:
            logger.info(f"Worker {worker_id} starting account {job.account_id}")
            job_fn(job.account_id)
            logger.info(f"Worker {worker_id} finished account {job.account_id}")
        except Exception as exc:
            logger.exception(f"Worker {worker_id} error on account {job.account_id}: {exc}")
        finally:
            task_queue.task_done()


def run_campaign_with_batch(account_ids: Iterable[int], batch_size: int, job_fn: Callable[[int], None]) -> None:
    q: queue.Queue = queue.Queue()
    for acc_id in account_ids:
        q.put(AccountJob(account_id=acc_id))

    stop_event = threading.Event()
    threads = []
    for i in range(max(1, int(batch_size))):
        t = threading.Thread(target=profile_worker, args=(q, i + 1, stop_event, job_fn), daemon=True)
        t.start()
        threads.append(t)

    q.join()
    stop_event.set()
    for t in threads:
        t.join()

