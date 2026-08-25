"""Retry Middleware with exponential backoff for transient step failures."""

import asyncio
from typing import Callable, Any
from app.core.logging import logger
from app.pipelines.base_step import BasePipelineStep
from app.pipelines.context import PipelineContext


class RetryMiddleware:
    """Retries a step on transient errors up to max_retries with exponential delay."""

    def __init__(self, max_retries: int = 2, base_delay: float = 0.5):
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def wrap(self, step: BasePipelineStep, context: PipelineContext, next_handler: Callable) -> Any:
        attempts = 0
        while True:
            try:
                return await next_handler(context)
            except Exception as e:
                attempts += 1
                if attempts > self.max_retries:
                    raise e
                delay = self.base_delay * (2 ** (attempts - 1))
                logger.warning(
                    f"[Retry] Step '{step.name}' failed (Attempt {attempts}/{self.max_retries}). Retrying in {delay}s: {e}"
                )
                await asyncio.sleep(delay)
