"""Unit tests for Multiprocessing and Compute Engine Providers."""

import pytest
from app.core.exceptions import FeatureDisabledError
from app.providers.compute import (
    ProcessPoolComputeEngine,
    RayComputeEngine,
    get_compute_engine,
)


def sample_math_task(x: int) -> int:
    return x * x + 10


@pytest.mark.asyncio
async def test_process_pool_compute_engine_execute():
    engine = ProcessPoolComputeEngine(max_workers=2)
    result = await engine.execute(sample_math_task, 5)
    assert result == 35


@pytest.mark.asyncio
async def test_process_pool_compute_engine_map():
    engine = ProcessPoolComputeEngine(max_workers=2)
    inputs = [1, 2, 3, 4]
    results = await engine.map(sample_math_task, inputs)
    assert results == [11, 14, 19, 26]


def test_default_compute_engine_factory():
    engine = get_compute_engine()
    assert engine.engine_type == "process_pool"


@pytest.mark.asyncio
async def test_ray_disabled_raises_feature_disabled_error():
    ray_engine = RayComputeEngine()
    with pytest.raises(FeatureDisabledError):
        await ray_engine.execute(sample_math_task, 5)
