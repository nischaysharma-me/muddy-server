# Architecture: Transactional Pipelines 🔄

## 1. Overview & Motivation

Complex AI computations often involve a sequence of interdependent steps:
1. Fetching external documents or API payloads.
2. Generating embeddings and performing vector searches.
3. Invoking LLM models to synthesize summaries or draft articles.
4. Generating image assets or social media threads.
5. Persisting final entities into relational databases and updating search indices.

If step 4 or 5 fails due to rate limits, network timeouts, or schema mismatches, standard systems leave partial records and orphaned assets in the database.

**Muddy Server's Transactional Pipeline Runner provides atomic execution semantics with automated, reverse-order compensating rollbacks.**

---

## 2. Pipeline Anatomy

Every pipeline step is represented by an implementation of `BasePipelineStep` in [`app/pipelines/base_step.py`](file:///Users/davinci/Documents/sscorp/nischaysharma.com/muddy-server/app/pipelines/base_step.py):

```python
from app.pipelines.context import PipelineContext

class BasePipelineStep:
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight

    async def validate(self, context: PipelineContext) -> bool:
        """Executed prior to execution. Returns False to halt pipeline cleanly."""
        return True

    async def execute(self, context: PipelineContext) -> Any:
        """Performs core computation and mutates context.outputs."""
        raise NotImplementedError

    async def rollback(self, context: PipelineContext) -> None:
        """Compensating action executed if a subsequent step in the pipeline fails."""
        pass
```

---

## 3. The Execution & Rollback Lifecycle

```
[START]
   │
   ▼
[Init DB Job] ──► Sets JobModel.status = "processing"
   │
   ▼
[Step 1: Validate] ──► [Step 1: Execute] ──► [Step 1: Log & Progress (33%)]
   │
   ▼
[Step 2: Validate] ──► [Step 2: Execute] ──► [Step 2: Log & Progress (66%)]
   │
   ▼
[Step 3: Validate] ──► [Step 3: FAILS ❌]
   │
   ├────────────────────────────────────────────────────────┐
   ▼                                                        ▼
[Step 2: Rollback 🔄]                              [Step 1: Rollback 🔄]
   │                                                        │
   └────────────────────────┬───────────────────────────────┘
                            ▼
                  [Mark Job FAILED ❌]
                  (Logs error to SQL)
```

### Forward Execution Flow:
1. **Pre-Validation (`validate`)**: Verifies all required input parameters and previous step outputs are present.
2. **Timing Middleware (`TimingMiddleware`)**: Measures step duration with microsecond precision using `time.perf_counter()`.
3. **Progress Telemetry (`ProgressTracker`)**: Calculates weighted percentage based on completed step weights and emits `job.progress` over the `EventBus`.
4. **Persistence (`_log_db_step`)**: Logs individual step status (`SUCCESS`), elapsed milliseconds, and parameters to `PipelineLogModel`.

### Compensating Reverse Rollback:
If an unhandled exception occurs at any point during step execution:
1. The runner halts forward execution immediately.
2. Gathers the list of **completed steps** in reverse order (`[Step 2, Step 1]`).
3. Asynchronously invokes `step.rollback(context)` on each step, allowing custom cleanup (e.g. deleting uploaded S3 files, reverting database records, clearing cache keys).
4. Updates SQL `JobModel.status = 'failed'` with the exact stack trace and emits `job.failed`.

---

## 4. Middleware Stack

- **`TimingMiddleware`**: Measures per-step latency and populates `context.metadata["step_durations"]`.
- **`RetryMiddleware`**: Wraps transient operations (e.g. external network calls) with exponential backoff:
  ```python
  from app.pipelines.middleware import RetryMiddleware

  retry_layer = RetryMiddleware(max_retries=3, base_delay=0.5)
  ```

---

## 5. Complete Practical Example

```python
from app.pipelines import BasePipelineStep, PipelineContext, PipelineRunner

class FetchDocumentStep(BasePipelineStep):
    def __init__(self):
        super().__init__(name="FetchDocument", weight=1.0)

    async def execute(self, context: PipelineContext):
        doc_id = context.inputs["doc_id"]
        context.outputs["raw_text"] = f"Document content for {doc_id}"
        return context.outputs["raw_text"]

    async def rollback(self, context: PipelineContext):
        context.outputs.pop("raw_text", None)


class GenerateSummaryStep(BasePipelineStep):
    def __init__(self):
        super().__init__(name="GenerateSummary", weight=2.0)

    async def execute(self, context: PipelineContext):
        text = context.outputs["raw_text"]
        context.outputs["summary"] = f"Summary of: {text}"
        return context.outputs["summary"]

    async def rollback(self, context: PipelineContext):
        context.outputs.pop("summary", None)


# Run the pipeline
runner = PipelineRunner("summary_pipeline", [
    FetchDocumentStep(),
    GenerateSummaryStep(),
])

context = await runner.run(inputs={"doc_id": "doc-9812"})
print(context.outputs["summary"])
```
