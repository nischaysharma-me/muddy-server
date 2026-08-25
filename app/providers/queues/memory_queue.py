"""In-Memory Asynchronous Job Queue."""

import asyncio
from typing import Any, Callable, Dict
from app.core.logging import logger
from app.providers.queues.base import BaseQueue


class MemoryQueue(BaseQueue):
    """Zero-dependency in-memory async queue for local development and testing."""

    def __init__(self):
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._statuses: Dict[str, str] = {}

    async def enqueue(
        self,
        job_id: str,
        task_func: Callable,
        payload: Dict[str, Any],
        **kwargs: Any,
    ) -> str:
        """Enqueues and spawns a non-blocking background task."""
        self._statuses[job_id] = "queued"

        async def worker_wrapper():
            self._statuses[job_id] = "processing"
            try:
                if asyncio.iscoroutinefunction(task_func):
                    await task_func(job_id, payload)
                else:
                    task_func(job_id, payload)
                self._statuses[job_id] = "completed"
            except asyncio.CancelledError:
                self._statuses[job_id] = "cancelled"
            except Exception as e:
                logger.error(f"[MemoryQueue] Job '{job_id}' failed: {e}")
                self._statuses[job_id] = "failed"
            finally:
                self._running_tasks.pop(job_id, None)

        task = asyncio.create_task(worker_wrapper())
        self._running_tasks[job_id] = task
        logger.debug(f"[MemoryQueue] Enqueued job '{job_id}'")
        return job_id

    async def get_status(self, job_id: str) -> str:
        return self._statuses.get(job_id, "not_found")

    async def cancel(self, job_id: str) -> bool:
        task = self._running_tasks.get(job_id)
        if task and not task.done():
            task.cancel()
            self._statuses[job_id] = "cancelled"
            return True
        return False

    @property
    def queue_type(self) -> str:
        return "memory"
