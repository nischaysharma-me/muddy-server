"""Redis and Arq Distributed Job Queue (Lazy-Loaded)."""

from typing import Any, Callable, Dict
from app.config import settings
from app.core.exceptions import FeatureDisabledError
from app.core.logging import logger
from app.providers.queues.base import BaseQueue


class RedisArqQueue(BaseQueue):
    """Distributed Redis-backed asynchronous task queue."""

    def __init__(self):
        self._is_connected = False
        self._redis_client = None

    async def _ensure_connected(self):
        if not settings.ENABLE_REDIS_QUEUE:
            raise FeatureDisabledError("REDIS_QUEUE")

        if self._is_connected and self._redis_client:
            return self._redis_client

        try:
            import redis.asyncio as aioredis
            self._redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            await self._redis_client.ping()
            self._is_connected = True
            logger.info(f"[RedisQueue] Connected to Redis queue at {settings.REDIS_URL}")
            return self._redis_client
        except ImportError as err:
            raise FeatureDisabledError("REDIS_QUEUE (redis package not installed)") from err
        except Exception as e:
            logger.error(f"[RedisQueue] Failed connecting to Redis: {e}")
            raise e

    async def enqueue(
        self,
        job_id: str,
        task_func: Callable,
        payload: Dict[str, Any],
        **kwargs: Any,
    ) -> str:
        redis = await self._ensure_connected()
        import json
        job_data = {
            "job_id": job_id,
            "status": "queued",
            "payload": payload,
        }
        await redis.hset(f"job:{job_id}", mapping={"data": json.dumps(job_data), "status": "queued"})
        await redis.lpush(settings.QUEUE_NAME, job_id)
        logger.info(f"[RedisQueue] Enqueued job '{job_id}' to Redis queue '{settings.QUEUE_NAME}'")
        return job_id

    async def get_status(self, job_id: str) -> str:
        redis = await self._ensure_connected()
        status = await redis.hget(f"job:{job_id}", "status")
        return status or "not_found"

    async def cancel(self, job_id: str) -> bool:
        redis = await self._ensure_connected()
        await redis.hset(f"job:{job_id}", "status", "cancelled")
        return True

    @property
    def queue_type(self) -> str:
        return "redis_arq"
