"""Ray Distributed Compute Engine (Lazy-Loaded)."""

import asyncio
from typing import Any, Callable, List, Optional
from app.config import settings
from app.core.exceptions import FeatureDisabledError
from app.core.logging import logger
from app.providers.compute.base import BaseComputeEngine


class RayComputeEngine(BaseComputeEngine):
    """Ray distributed compute engine with lazy cluster initialization and actor pooling."""

    def __init__(self):
        self._is_initialized = False
        self._ray_module = None

    def _ensure_ray_initialized(self):
        """Lazily imports and connects to Ray only when explicitly called."""
        if not settings.ENABLE_RAY_COMPUTE:
            raise FeatureDisabledError("RAY_COMPUTE")

        if self._is_initialized and self._ray_module:
            return self._ray_module

        try:
            import ray
            self._ray_module = ray

            if not ray.is_initialized():
                init_kwargs = {
                    "include_dashboard": settings.RAY_INCLUDE_DASHBOARD,
                    "log_to_driver": settings.RAY_LOG_TO_DRIVER,
                }
                if settings.RAY_ADDRESS:
                    init_kwargs["address"] = settings.RAY_ADDRESS
                if settings.RAY_NUM_CPUS:
                    init_kwargs["num_cpus"] = settings.RAY_NUM_CPUS
                if settings.RAY_NUM_GPUS:
                    init_kwargs["num_gpus"] = settings.RAY_NUM_GPUS

                ray.init(**init_kwargs)
                logger.info(f"🚀 [Ray] Ray cluster initialized successfully (Dashboard: {settings.RAY_INCLUDE_DASHBOARD})")

            self._is_initialized = True
            return ray
        except ImportError as err:
            logger.error(f"[Ray] ray library is not installed: {err}")
            raise FeatureDisabledError("RAY_COMPUTE (ray package not installed)") from err
        except Exception as e:
            logger.error(f"[Ray] Failed to initialize Ray cluster: {e}")
            raise e

    async def execute(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Executes a function across Ray distributed workers."""
        ray = self._ensure_ray_initialized()
        remote_fn = ray.remote(func)
        future = remote_fn.remote(*args, **kwargs)
        # Convert ray ObjectRef to asyncio future
        return await asyncio.wrap_future(future.future())

    async def map(self, func: Callable, items: List[Any]) -> List[Any]:
        """Maps a function across Ray distributed workers in parallel."""
        ray = self._ensure_ray_initialized()
        remote_fn = ray.remote(func)
        futures = [remote_fn.remote(item) for item in items]
        return await asyncio.gather(*[asyncio.wrap_future(f.future()) for f in futures])

    def shutdown(self):
        """Shuts down local Ray cluster if initialized."""
        if self._is_initialized and self._ray_module:
            if self._ray_module.is_initialized():
                self._ray_module.shutdown()
                logger.info("[Ray] Ray cluster shutdown completed.")
            self._is_initialized = False

    @property
    def engine_type(self) -> str:
        return "ray_distributed"
