"""Abstract Base Queue Interface."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional


class BaseQueue(ABC):
    """Abstract interface for asynchronous job queues."""

    @abstractmethod
    async def enqueue(
        self,
        job_id: str,
        task_func: Callable,
        payload: Dict[str, Any],
        **kwargs: Any,
    ) -> str:
        """Enqueues a task for background asynchronous execution."""
        raise NotImplementedError

    @abstractmethod
    async def get_status(self, job_id: str) -> str:
        """Retrieves current execution status of a queued job."""
        raise NotImplementedError

    @abstractmethod
    async def cancel(self, job_id: str) -> bool:
        """Cancels a pending or running job."""
        raise NotImplementedError

    @property
    @abstractmethod
    def queue_type(self) -> str:
        """Returns the type identifier of this queue."""
        raise NotImplementedError
