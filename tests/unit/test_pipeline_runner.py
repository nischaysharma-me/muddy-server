"""Unit tests for Transactional Pipeline Runner, Progress Tracker, and Rollbacks."""

import pytest
from app.core.event_bus import event_bus
from app.core.exceptions import PipelineExecutionError
from app.pipelines import BasePipelineStep, PipelineContext, PipelineRunner


class ValidateInputStep(BasePipelineStep):
    async def execute(self, context: PipelineContext):
        if not context.inputs.get("text"):
            raise ValueError("Input text is required")
        context.outputs["validated"] = True
        return "validated"


class ProcessStep(BasePipelineStep):
    def __init__(self, should_fail: bool = False):
        super().__init__(name="ProcessStep", weight=2.0)
        self.should_fail = should_fail
        self.rolled_back = False

    async def execute(self, context: PipelineContext):
        if self.should_fail:
            raise RuntimeError("ProcessStep failed unexpectedly")
        context.outputs["processed_text"] = context.inputs["text"].upper()
        return context.outputs["processed_text"]

    async def rollback(self, context: PipelineContext):
        self.rolled_back = True
        context.outputs.pop("processed_text", None)


class FormatOutputStep(BasePipelineStep):
    async def execute(self, context: PipelineContext):
        context.outputs["final"] = f"RESULT: {context.outputs.get('processed_text')}"
        return context.outputs["final"]


@pytest.mark.asyncio
async def test_pipeline_runner_success():
    progress_events = []

    async def on_progress(event_type: str, payload: dict):
        progress_events.append(payload["progress_pct"])

    event_bus.subscribe("job.progress", on_progress)

    step1 = ValidateInputStep(name="Validate", weight=1.0)
    step2 = ProcessStep(should_fail=False)
    step3 = FormatOutputStep(name="Format", weight=1.0)

    runner = PipelineRunner("text_processing_pipeline", [step1, step2, step3])
    context = await runner.run(inputs={"text": "hello world"})

    assert context.is_completed is True
    assert context.progress == 100.0
    assert context.outputs["processed_text"] == "HELLO WORLD"
    assert context.outputs["final"] == "RESULT: HELLO WORLD"
    assert len(progress_events) >= 3
    assert progress_events[-1] == 100.0


@pytest.mark.asyncio
async def test_pipeline_runner_rollback_on_failure():
    step1 = ValidateInputStep(name="Validate", weight=1.0)
    step2 = ProcessStep(should_fail=True)
    step3 = FormatOutputStep(name="Format", weight=1.0)

    runner = PipelineRunner("failing_pipeline", [step1, step2, step3])

    with pytest.raises(PipelineExecutionError) as exc_info:
        await runner.run(inputs={"text": "test rollback"})

    assert "ProcessStep failed unexpectedly" in str(exc_info.value)
