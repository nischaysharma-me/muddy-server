# Architecture: Transactional Pipelines 🔄

Muddy Server features an execution framework designed for multi-step data transformations and LLM agent pipelines where state consistency and rollback guarantees are required.

---

## 🏗️ Core Pipeline Lifecycle

1. **Initialization**:
   - `PipelineRunner` initializes a `JobModel` record in SQL with status `processing`.
   - Emits `job.started` across `EventBus`.
2. **Step Execution Loop**:
   - For each step:
     - Pre-Validation: Calls `step.validate(context)`.
     - Timing Middleware: Measures duration in milliseconds.
     - Execution: Runs `step.execute(context)`.
     - Progress: Computes weighted `0.0 - 100.0%` progress and emits `job.progress`.
     - Log: Writes execution trace to `PipelineLogModel`.
3. **Rollback on Failure**:
   - If any step raises an exception:
     - The runner halts forward execution.
     - Automatically calls `step.rollback(context)` in **reverse order** on all previously completed steps.
     - Marks SQL `JobModel.status = 'failed'` and emits `job.failed`.
4. **Completion**:
   - Marks SQL `JobModel.status = 'completed'`, updates outputs, and emits `job.completed`.
