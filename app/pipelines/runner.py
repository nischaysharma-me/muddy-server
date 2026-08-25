"""Transactional Pipeline Runner with Lifecycle Hooks and Rollbacks."""

import time
from typing import Any, List, Optional
from app.config import settings
from app.core.event_bus import event_bus
from app.core.exceptions import PipelineExecutionError
from app.core.logging import logger
from app.pipelines.base_step import BasePipelineStep
from app.pipelines.context import PipelineContext
from app.pipelines.middleware.timing import TimingMiddleware
from app.pipelines.progress import ProgressTracker


class PipelineRunner:
    """Orchestrates transactional multi-step pipelines with automated SQL tracking and rollbacks."""

    def __init__(self, name: str, steps: List[BasePipelineStep]):
        self.name = name
        self.steps = steps
        weights = [s.weight for s in steps]
        self.progress_tracker = ProgressTracker(weights)

    async def run(self, context: Optional[PipelineContext] = None, inputs: Optional[dict] = None) -> PipelineContext:
        """Executes the pipeline sequentially with transaction wrapping and rollback hooks."""
        ctx = context or PipelineContext(pipeline_name=self.name, inputs=inputs or {})
        ctx.pipeline_name = self.name
        completed_steps: List[BasePipelineStep] = []

        logger.info(f"🚀 [Pipeline] Starting pipeline '{self.name}' (Job ID: {ctx.job_id})")

        # 1. Initialize Job in SQL if DB is enabled
        await self._init_db_job(ctx)

        # 2. Emit Job Started Event
        await event_bus.emit("job.started", {
            "job_id": ctx.job_id,
            "pipeline_name": self.name,
            "trace_id": ctx.trace_id,
        })

        try:
            for idx, step in enumerate(self.steps):
                ctx.stage = f"STEP_{idx + 1}_{step.name.upper()}"

                # Step Pre-Validation
                is_valid = await step.validate(ctx)
                if not is_valid:
                    raise PipelineExecutionError(
                        f"Validation failed for step '{step.name}'",
                        step_name=step.name,
                    )

                # Execute with Timing Middleware
                async def execute_step(c: PipelineContext):
                    return await step.execute(c)

                step_result = await TimingMiddleware.wrap(step, ctx, execute_step)
                ctx.step_results[step.name] = step_result
                completed_steps.append(step)

                # Progress & Telemetry Update
                duration = ctx.metadata.get("step_durations", {}).get(step.name, 0.0)
                await self.progress_tracker.update_step(idx, step.name, ctx)
                await self._log_db_step(ctx, step.name, "SUCCESS", duration)

            # Mark Completed
            ctx.is_completed = True
            ctx.progress = 100.0
            ctx.stage = "COMPLETED"
            ctx.end_time = time.perf_counter()

            # Update DB Job
            await self._update_db_job_success(ctx)

            # Emit Final Success Event
            await event_bus.emit("job.completed", {
                "job_id": ctx.job_id,
                "pipeline_name": self.name,
                "progress_pct": 100.0,
                "elapsed_ms": ctx.elapsed_ms(),
                "outputs": ctx.outputs,
            })

            logger.info(f"✅ [Pipeline] Pipeline '{self.name}' completed in {ctx.elapsed_ms()}ms")
            return ctx

        except Exception as e:
            ctx.is_failed = True
            ctx.error = str(e)
            ctx.stage = "FAILED"
            ctx.end_time = time.perf_counter()

            logger.error(f"❌ [Pipeline] Pipeline '{self.name}' failed at step: {e}")

            # Execute Rollbacks in Reverse Order
            await self._rollback_completed_steps(completed_steps, ctx)

            # Update DB Job Status
            await self._update_db_job_failed(ctx)

            # Emit Failure Event
            await event_bus.emit("job.failed", {
                "job_id": ctx.job_id,
                "pipeline_name": self.name,
                "error": str(e),
                "elapsed_ms": ctx.elapsed_ms(),
            })

            raise PipelineExecutionError(
                f"Pipeline '{self.name}' failed: {str(e)}",
                details={"job_id": ctx.job_id, "error": str(e)},
            ) from e

    async def _rollback_completed_steps(self, completed_steps: List[BasePipelineStep], ctx: PipelineContext):
        """Executes rollbacks in reverse order on all completed steps."""
        for step in reversed(completed_steps):
            try:
                logger.warning(f"🔄 [Rollback] Executing rollback on step '{step.name}'")
                await step.rollback(ctx)
            except Exception as rb_err:
                logger.error(f"⚠️ [Rollback] Error in rollback for step '{step.name}': {rb_err}")

    async def _init_db_job(self, ctx: PipelineContext):
        if not settings.ENABLE_SQL_DB:
            return
        try:
            from app.db.session import async_session_factory
            from app.db.models.job import JobModel
            async with async_session_factory() as session:
                async with session.begin():
                    job = JobModel(
                        id=ctx.job_id,
                        status="processing",
                        progress=0.0,
                        stage=ctx.stage,
                        job_type=self.name,
                        trace_id=ctx.trace_id,
                        payload=ctx.inputs,
                    )
                    session.add(job)
        except Exception as e:
            logger.warning(f"[DB] Could not initialize SQL job record: {e}")

    async def _log_db_step(self, ctx: PipelineContext, step_name: str, status: str, duration_ms: float):
        if not settings.ENABLE_SQL_DB:
            return
        try:
            from app.db.session import async_session_factory
            from app.db.models.pipeline_log import PipelineLogModel
            async with async_session_factory() as session:
                async with session.begin():
                    log = PipelineLogModel(
                        job_id=ctx.job_id,
                        pipeline_name=self.name,
                        step_name=step_name,
                        status=status,
                        duration_ms=duration_ms,
                    )
                    session.add(log)
        except Exception as e:
            logger.warning(f"[DB] Could not log pipeline step to SQL: {e}")

    async def _update_db_job_success(self, ctx: PipelineContext):
        if not settings.ENABLE_SQL_DB:
            return
        try:
            from sqlalchemy import select
            from app.db.session import async_session_factory
            from app.db.models.job import JobModel
            async with async_session_factory() as session:
                async with session.begin():
                    stmt = select(JobModel).where(JobModel.id == ctx.job_id)
                    job = await session.scalar(stmt)
                    if job:
                        job.status = "completed"
                        job.progress = 100.0
                        job.stage = "COMPLETED"
                        job.result = ctx.outputs
                        job.execution_time_ms = ctx.elapsed_ms()
        except Exception as e:
            logger.warning(f"[DB] Could not update completed job in SQL: {e}")

    async def _update_db_job_failed(self, ctx: PipelineContext):
        if not settings.ENABLE_SQL_DB:
            return
        try:
            from sqlalchemy import select
            from app.db.session import async_session_factory
            from app.db.models.job import JobModel
            async with async_session_factory() as session:
                async with session.begin():
                    stmt = select(JobModel).where(JobModel.id == ctx.job_id)
                    job = await session.scalar(stmt)
                    if job:
                        job.status = "failed"
                        job.stage = "FAILED"
                        job.error = ctx.error
                        job.execution_time_ms = ctx.elapsed_ms()
        except Exception as e:
            logger.warning(f"[DB] Could not update failed job in SQL: {e}")
