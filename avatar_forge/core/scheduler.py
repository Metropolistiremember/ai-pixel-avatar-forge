"""RenderScheduler — bounded thread pool for pixel render jobs."""
from __future__ import annotations

import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Callable, TypeVar

from avatar_forge.contracts.jobs import RenderJob, RenderResult
from avatar_forge.utils.logging import get_logger

log = get_logger(__name__)
T = TypeVar("T")


class RenderScheduler:
    """Serializes GPU-touching work behind a semaphore, fans out CPU work."""

    def __init__(self, max_workers: int = 2, gpu_slots: int = 1) -> None:
        self._pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="forge-render")
        self._gpu_gate = threading.Semaphore(gpu_slots)
        self._inflight: set[Future[RenderResult]] = set()

    def submit(self, job: RenderJob, fn: Callable[[RenderJob], RenderResult]) -> Future[RenderResult]:

        def _run() -> RenderResult:
            if job.uses_gpu:
                with self._gpu_gate:
                    return fn(job)
            return fn(job)

        fut = self._pool.submit(_run)
        self._inflight.add(fut)
        fut.add_done_callback(self._inflight.discard)
        return fut

    def drain(self, timeout: float = 30.0) -> None:
        for fut in list(self._inflight):
            try:
                fut.result(timeout=timeout)
            except Exception as exc:  # noqa: BLE001
                log.warning("in-flight job failed during drain: %s", exc)
        self._pool.shutdown(wait=True, cancel_futures=False)