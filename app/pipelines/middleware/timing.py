"""Timing Middleware for measuring execution duration per step."""

import time
from typing import Callable, Any
from app.pipelines.base_step import BasePipelineStep
from app.pipelines.context import PipelineContext


class TimingMiddleware:
    """Measures precise step execution duration in milliseconds."""

    @staticmethod
    async def wrap(step: BasePipelineStep, context: PipelineContext, next_handler: Callable) -> Any:
        start = time.perf_counter()
        result = await next_handler(context)
        duration_ms = round((time.perf_counter() - start) * 1000.0, 2)
        if "step_durations" not in context.metadata:
            context.metadata["step_durations"] = {}
        context.metadata["step_durations"][step.name] = duration_ms
        return result
