# Guide: Creating Transactional Pipelines 🔄

This tutorial guides you through building a resilient, multi-step **Article Generation & Social Syndication Pipeline** using Muddy Server's `PipelineRunner`.

---

## 1. Concepts Review

A transactional pipeline is composed of:
1. **`PipelineContext`**: A shared state container holding `inputs`, `outputs`, `metadata`, and execution logs across all steps.
2. **`BasePipelineStep`**: An atomic unit of work with 3 mandatory hooks:
   - `validate(context)`: Pre-execution assertion.
   - `execute(context)`: Forward execution logic.
   - `rollback(context)`: Reverse compensating action on failure.
3. **`PipelineRunner`**: Orchestrator executing steps sequentially with weighted progress tracking and automated rollback recovery.

---

## 2. Step 1: Article Synthesis Step

```python
from app.pipelines import BasePipelineStep, PipelineContext
from app.services.llm_service import llm_service

class SynthesizeArticleStep(BasePipelineStep):
    def __init__(self):
        super().__init__(name="SynthesizeArticle", weight=2.0)

    async def validate(self, context: PipelineContext) -> bool:
        return "topic" in context.inputs and len(context.inputs["topic"]) > 3

    async def execute(self, context: PipelineContext):
        topic = context.inputs["topic"]
        prompt = f"Write a comprehensive technical article on '{topic}'."
        
        # Use centralized OpenRouter via LLMService
        result = await llm_service.generate(prompt=prompt, model="claude-3.5-sonnet")
        context.outputs["article_text"] = result["content"]
        return context.outputs["article_text"]

    async def rollback(self, context: PipelineContext):
        # Clear generated article from context
        context.outputs.pop("article_text", None)
```

---

## 3. Step 2: Social Thread Generation Step

```python
class GenerateSocialThreadStep(BasePipelineStep):
    def __init__(self):
        super().__init__(name="GenerateSocialThread", weight=1.0)

    async def validate(self, context: PipelineContext) -> bool:
        return "article_text" in context.outputs

    async def execute(self, context: PipelineContext):
        article = context.outputs["article_text"]
        prompt = f"Convert this article into a 5-tweet viral thread:\n\n{article[:1000]}"
        
        result = await llm_service.generate(prompt=prompt, model="gpt-4o-mini")
        context.outputs["social_thread"] = result["content"]
        return context.outputs["social_thread"]

    async def rollback(self, context: PipelineContext):
        context.outputs.pop("social_thread", None)
```

---

## 4. Step 3: Database Entity Persistence Step

```python
from app.db.models.job import JobModel
from app.db.session import async_session_factory

class PersistToDatabaseStep(BasePipelineStep):
    def __init__(self):
        super().__init__(name="PersistToDatabase", weight=1.0)

    async def execute(self, context: PipelineContext):
        # Persist generated outputs
        context.outputs["saved_entity_id"] = "post-98421"
        return context.outputs["saved_entity_id"]

    async def rollback(self, context: PipelineContext):
        entity_id = context.outputs.get("saved_entity_id")
        if entity_id:
            # Delete or soft-delete entity from database
            print(f"🧹 [Rollback] Cleaning up created entity '{entity_id}'")
            context.outputs.pop("saved_entity_id", None)
```

---

## 5. Executing the Pipeline

```python
from app.pipelines import PipelineRunner

async def run_content_pipeline():
    runner = PipelineRunner(
        pipeline_name="article_and_social_generation",
        steps=[
            SynthesizeArticleStep(),
            GenerateSocialThreadStep(),
            PersistToDatabaseStep(),
        ]
    )

    context = await runner.run(inputs={"topic": "Event-Driven State Machines with LangGraph"})
    
    if context.status == "completed":
        print("✅ Pipeline Completed Successfully!")
        print("Article Length:", len(context.outputs["article_text"]))
        print("Social Thread:", context.outputs["social_thread"])
    else:
        print("❌ Pipeline Failed and was Rolled Back. Error:", context.error)

# Run with asyncio
import asyncio
asyncio.run(run_content_pipeline())
```

---

## 6. Real-Time Telemetry During Execution

While `runner.run()` is executing:
1. `EventBus` broadcasts `job.progress` after every step with weighted percentages (`40%`, `60%`, `100%`).
2. Connected WebSockets on `/api/v1/ws/jobs/{job_id}` receive real-time UI updates automatically.
3. Every step duration and status is permanently recorded in the SQL table `pipeline_logs`.
