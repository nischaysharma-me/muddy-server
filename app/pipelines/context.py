"""Pipeline Execution Context."""

import time
import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class PipelineContext(BaseModel):
    """Encapsulates the state, inputs, outputs, and telemetry across pipeline steps."""

    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pipeline_name: str = Field(default="generic_pipeline")
    session_id: Optional[str] = Field(default=None)
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stage: str = Field(default="INITIALIZING")
    progress: float = Field(default=0.0, ge=0.0, le=100.0)

    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    step_results: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    start_time: float = Field(default_factory=time.perf_counter)
    end_time: Optional[float] = None
    is_completed: bool = False
    is_failed: bool = False
    error: Optional[str] = None

    def elapsed_ms(self) -> float:
        """Calculates elapsed execution time in milliseconds."""
        current = self.end_time if self.end_time else time.perf_counter()
        return round((current - self.start_time) * 1000.0, 2)
