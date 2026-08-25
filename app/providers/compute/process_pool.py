"""Lightweight Multiprocessing Compute Engine."""

import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any, Callable, List
from app.providers.compute.base import BaseComputeEngine


class ProcessPoolComputeEngine(BaseComputeEngine):
    """Zero-overhead parallel compute engine using standard Python multiprocessing and thread pools."""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)

    async def execute(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Executes a function in the worker pool without blocking the async event loop."""
        loop = asyncio.get_running_loop()
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)

        def runner():
            return func(*args, **kwargs)

        return await loop.run_in_executor(self._thread_pool, runner)

    async def map(self, func: Callable, items: List[Any]) -> List[Any]:
        """Runs parallel executions concurrently over a list of items using asyncio.gather."""
        tasks = [self.execute(func, item) for item in items]
        return await asyncio.gather(*tasks)

    @property
    def engine_type(self) -> str:
        return "process_pool"
