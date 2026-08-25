# Guide: Feature Flags & Zero-RAM Optimization ⚙️

## 1. The RAM Problem in Modern Python Backends

In Python, importing heavy machine learning, scientific computing, or distributed frameworks loads shared C-extensions, CUDA libraries, and pre-allocated memory pools immediately into the master process:

| Library Import | Startup Process RAM Impact |
| :--- | :--- |
| `import torch` | **+400 MB to +700 MB** |
| `import transformers` / `sentence_transformers` | **+300 MB** (Loads tokenizer weights & model graphs) |
| `import ray; ray.init()` | **+500 MB to +1.2 GB** (Spawns GCS server, plasma store, raylet daemons) |

When you only need to run an **LLM Agent Gateway**, **WebSocket telemetry hub**, and **FastAPI REST endpoints**, carrying a **1.5 GB to 2.0 GB memory footprint** per worker process is inefficient and costly.

---

## 2. Muddy Server's Zero-RAM Guarantee

Muddy Server strictly decouples lightweight web/agent operations from heavy compute tiers through **Feature Flags** and **Lazy Subsystem Loading**.

```
                           ┌──────────────────────────────┐
                           │    FastAPI Process Memory    │
                           └──────────────┬───────────────┘
                                          │
            ┌─────────────────────────────┴─────────────────────────────┐
            ▼                                                           ▼
 Lightweight Mode (Default)                                   Heavy Compute Mode
 - ENABLE_ML_TRANSFORMERS=false                               - ENABLE_ML_TRANSFORMERS=true
 - ENABLE_RAY_COMPUTE=false                                   - ENABLE_RAY_COMPUTE=true
 - ENABLE_REDIS_QUEUE=false                                   - ENABLE_REDIS_QUEUE=true
 ──────────────────────────────────                           ──────────────────────────────────
 Memory Footprint: ~50 MB                                     Memory Footprint: ~1.2 GB+
 Modules Loaded: FastAPI, LangChain Core,                     Modules Loaded: PyTorch,
                 aiosqlite, Uvicorn                                           HuggingFace, Ray Actors
```

---

## 3. Environment Variables Reference

Edit your `.env` file to toggle subsystems:

```env
# -------------------------------------------------------------
# CORE APPLICATION SUBSYSTEMS (Lightweight, < 50MB RAM)
# -------------------------------------------------------------
ENABLE_LLM_GATEWAY=true     # Multi-model LLM generation & OpenRouter
ENABLE_AGENTS=true          # LangGraph ReAct agents & cyclic state graphs
ENABLE_WEBSOCKETS=true      # Live WebSocket telemetry & progress broadcaster
ENABLE_SQL_DB=true          # SQLAlchemy 2.0 Async database persistence
ENABLE_DOCS_ENGINE=true     # Markdown documentation portal & APIs

# -------------------------------------------------------------
# HEAVY COMPUTE SUBSYSTEMS (Toggle on only when required)
# -------------------------------------------------------------
ENABLE_ML_TRANSFORMERS=false # PyTorch & HuggingFace Dense Vector Embeddings
ENABLE_RAY_COMPUTE=false     # Ray Distributed Cluster Actor Pool
ENABLE_REDIS_QUEUE=false     # Redis Arq Distributed Background Queue
```

---

## 4. How Lazy Loading Works Under the Hood

In [`app/providers/ml/transformer_embeddings.py`](file:///Users/davinci/Documents/sscorp/nischaysharma.com/muddy-server/app/providers/ml/transformer_embeddings.py):

```python
def _ensure_model_loaded(self):
    # 1. Check feature flag before attempting import
    if not settings.ENABLE_ML_TRANSFORMERS:
        raise FeatureDisabledError("ML_TRANSFORMERS")

    if self._model is not None:
        return self._model

    # 2. Lazy import occurs ONLY when invoked and enabled
    from sentence_transformers import SentenceTransformer
    self._model = SentenceTransformer(self.model_name)
    return self._model
```

If an endpoint requiring a disabled feature is called, the server responds with a clean `FeatureDisabledError` (`403 Forbidden` / `400 Bad Request`) without crashing or leaking memory.
