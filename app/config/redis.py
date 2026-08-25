"""Redis and Async Job Queue Settings."""

from pydantic import Field
from app.config.base import BaseSettings


class RedisSettings(BaseSettings):
    """Configuration for Redis cache and Arq distributed queues."""

    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    QUEUE_NAME: str = Field(
        default="muddy_compute_queue",
        description="Default queue name for async jobs",
    )
    DEFAULT_JOB_TIMEOUT: int = Field(
        default=300,
        description="Job execution timeout in seconds",
    )
