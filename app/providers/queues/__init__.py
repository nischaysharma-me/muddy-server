"""Job Queue Provider Package."""

from app.config import settings
from app.providers.queues.base import BaseQueue
from app.providers.queues.memory_queue import MemoryQueue
from app.providers.queues.redis_queue import RedisArqQueue

_default_memory_queue: MemoryQueue = None
_default_redis_queue: RedisArqQueue = None


def get_job_queue() -> BaseQueue:
    """Factory returning the active job queue based on configuration."""
    global _default_memory_queue, _default_redis_queue

    if settings.ENABLE_REDIS_QUEUE:
        if _default_redis_queue is None:
            _default_redis_queue = RedisArqQueue()
        return _default_redis_queue

    if _default_memory_queue is None:
        _default_memory_queue = MemoryQueue()
    return _default_memory_queue


__all__ = [
    "BaseQueue",
    "MemoryQueue",
    "RedisArqQueue",
    "get_job_queue",
]
