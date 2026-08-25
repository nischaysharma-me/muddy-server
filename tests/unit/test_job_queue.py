"""Unit tests for Asynchronous Job Queue and JobService."""

import asyncio
import pytest
from app.db.session import init_db
from app.services.job_service import job_service


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()


@pytest.mark.asyncio
async def test_job_service_create_and_execute():
    executed = False

    async def mock_background_compute(job_id: str, payload: dict):
        nonlocal executed
        await asyncio.sleep(0.05)
        executed = True

    # 1. Enqueue job
    job_id = await job_service.create_and_enqueue(
        job_type="heavy_simulation",
        payload={"iterations": 100},
        task_func=mock_background_compute,
    )

    assert job_id is not None

    # 2. Check initial status
    initial_status = await job_service.get_job(job_id)
    assert initial_status["status"] in ["queued", "processing", "completed"]

    # 3. Wait for background task to finish
    await asyncio.sleep(0.1)
    assert executed is True


@pytest.mark.asyncio
async def test_job_cancellation():
    async def long_running_task(job_id: str, payload: dict):
        await asyncio.sleep(2.0)

    job_id = await job_service.create_and_enqueue(
        job_type="long_task",
        payload={},
        task_func=long_running_task,
    )

    cancelled = await job_service.cancel_job(job_id)
    assert cancelled is True

    status_data = await job_service.get_job(job_id)
    assert status_data["status"] == "cancelled"
