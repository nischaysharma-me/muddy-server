"""Compute and Multiprocessing Provider Package."""

from app.config import settings
from app.providers.compute.base import BaseComputeEngine
from app.providers.compute.process_pool import ProcessPoolComputeEngine
from app.providers.compute.ray_client import RayComputeEngine

_default_process_pool: ProcessPoolComputeEngine = None
_default_ray_engine: RayComputeEngine = None


def get_compute_engine() -> BaseComputeEngine:
    """Factory returning the active compute engine based on configuration."""
    global _default_process_pool, _default_ray_engine

    if settings.ENABLE_RAY_COMPUTE:
        if _default_ray_engine is None:
            _default_ray_engine = RayComputeEngine()
        return _default_ray_engine

    if _default_process_pool is None:
        _default_process_pool = ProcessPoolComputeEngine()
    return _default_process_pool


__all__ = [
    "BaseComputeEngine",
    "ProcessPoolComputeEngine",
    "RayComputeEngine",
    "get_compute_engine",
]
