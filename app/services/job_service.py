"""Job Lifecycle and Queue Management Service."""

import uuid
from typing import Any, Callable, Dict, Optional
from sqlalchemy import select
from app.config import settings
from app.core.event_bus import event_bus
from app.core.logging import logger
from app.db.models.job import JobModel
from app.db.session import async_session_factory
from app.providers.queues import get_job_queue
from app.services.base_service import BaseService


class JobService(BaseService):
    """Orchestrates job lifecycle across SQL persistence, Redis/Memory queue, and EventBus."""

    def __init__(self):
        super().__init__("JobService")
        self.queue = get_job_queue()

    async def create_and_enqueue(
        self,
        job_type: str,
        payload: Dict[str, Any],
        task_func: Callable,
        job_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> str:
        """Persists job metadata in SQL and enqueues it for background execution."""
        assigned_id = job_id or str(uuid.uuid4())
        assigned_trace = trace_id or str(uuid.uuid4())

        # 1. Create SQL record if DB is enabled
        if settings.ENABLE_SQL_DB:
            async with async_session_factory() as session:
                async with session.begin():
                    job_record = JobModel(
                        id=assigned_id,
                        status="queued",
                        progress=0.0,
                        stage="QUEUED",
                        job_type=job_type,
                        trace_id=assigned_trace,
                        payload=payload,
                    )
                    session.add(job_record)

        # 2. Enqueue in background queue
        await self.queue.enqueue(assigned_id, task_func, payload)

        # 3. Emit Event
        await event_bus.emit("job.queued", {
            "job_id": assigned_id,
            "job_type": job_type,
            "trace_id": assigned_trace,
            "status": "QUEUED",
        })

        logger.info(f"📥 [JobService] Created and enqueued job '{assigned_id}' ({job_type})")
        return assigned_id

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves latest job status, progress, and result."""
        if settings.ENABLE_SQL_DB:
            async with async_session_factory() as session:
                stmt = select(JobModel).where(JobModel.id == job_id)
                job = await session.scalar(stmt)
                if job:
                    return {
                        "job_id": job.id,
                        "status": job.status,
                        "progress": job.progress,
                        "stage": job.stage,
                        "job_type": job.job_type,
                        "result": job.result,
                        "error": job.error,
                        "execution_time_ms": job.execution_time_ms,
                        "created_at": job.created_at.isoformat() if job.created_at else None,
                        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
                    }

        # Fallback to queue status
        status = await self.queue.get_status(job_id)
        return {
            "job_id": job_id,
            "status": status,
            "progress": 100.0 if status == "completed" else 0.0,
        }

    async def cancel_job(self, job_id: str) -> bool:
        """Cancels a job in queue and marks SQL record as cancelled."""
        cancelled = await self.queue.cancel(job_id)
        if settings.ENABLE_SQL_DB:
            async with async_session_factory() as session:
                async with session.begin():
                    stmt = select(JobModel).where(JobModel.id == job_id)
                    job = await session.scalar(stmt)
                    if job:
                        job.status = "cancelled"
                        job.stage = "CANCELLED"
        return cancelled


job_service = JobService()
