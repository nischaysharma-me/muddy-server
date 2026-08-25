# Guide: Creating Transactional Pipelines 🔄

How to create transactional multi-step pipelines with automatic reverse-order rollbacks.

---

## 1. Define Custom Pipeline Steps
Subclass `BasePipelineStep`:

```python
from app.pipelines import BasePipelineStep, PipelineContext

class FetchArticleContentStep(BasePipelineStep):
    def __init__(self):
        super().__init__(name="FetchContent", weight=1.0)

    async def validate(self, context: PipelineContext) -> bool:
        return "url" in context.inputs

    async def execute(self, context: PipelineContext):
        url = context.inputs["url"]
        # Fetch content logic
        context.outputs["raw_content"] = "Extracted text..."
        return context.outputs["raw_content"]

    async def rollback(self, context: PipelineContext):
        # Compensating action if downstream step fails
        context.outputs.pop("raw_content", None)
```

---

## 2. Execute via PipelineRunner
```python
from app.pipelines import PipelineRunner

runner = PipelineRunner("article_enrichment", [
    FetchArticleContentStep(),
    SummarizeWithLLMStep(),
    PersistToDatabaseStep(),
])

context = await runner.run(inputs={"url": "https://example.com/post"})
print("Completed:", context.outputs)
```
