"""Progress Tracking and Event Emitter."""

from typing import List, Optional
from app.core.event_bus import event_bus
from app.core.logging import logger
from app.pipelines.context import PipelineContext


class ProgressTracker:
    """Calculates weighted 0–100% progress and emits telemetry events via EventBus."""

    def __init__(self, step_weights: List[float]):
        self.step_weights = step_weights
        self.total_weight = sum(step_weights) if step_weights else 1.0
        self.completed_weight = 0.0

    async def update_step(
        self,
        step_index: int,
        step_name: str,
        context: PipelineContext,
        stage: Optional[str] = None,
    ) -> float:
        """Updates progress on step completion and emits progress event."""
        if step_index < len(self.step_weights):
            self.completed_weight += self.step_weights[step_index]

        calculated_pct = min(100.0, round((self.completed_weight / self.total_weight) * 100.0, 1))
        context.progress = calculated_pct
        context.stage = stage or step_name

        payload = {
            "job_id": context.job_id,
            "pipeline_name": context.pipeline_name,
            "session_id": context.session_id,
            "trace_id": context.trace_id,
            "stage": context.stage,
            "progress_pct": context.progress,
            "elapsed_ms": context.elapsed_ms(),
            "status": "PROCESSING",
        }

        # Emit progress event across EventBus (to WebSockets / telemetry)
        await event_bus.emit("job.progress", payload)
        logger.debug(f"[Progress] Job {context.job_id} -> {context.stage} ({context.progress}%)")
        return calculated_pct
