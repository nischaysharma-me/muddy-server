# About Muddy Server 🚀

## Executive Summary

**Muddy Server** is a high-performance, modular **Computation-as-a-Service (CaaS)** and AI orchestration backend built with **Python 3.12**, **FastAPI**, **SQLAlchemy 2.0 Async**, **LangGraph**, and **OpenRouter**.

It was built as an isolated companion service to downstream web and backend applications (such as `nischaysharma-server` and web clients) to provide heavy computation, multi-model AI reasoning, transactional data pipelines, and real-time telemetry without bloating the primary application codebase.

---

## 🎯 The Core Problem & Solution

### The Problem
Modern web backends often suffer from architectural bloat when AI agents, ML transformer embeddings, and distributed multiprocessing are bundled directly into the primary application server:
- **RAM Explosion**: Importing PyTorch, Transformers, or Ray at startup consumes **1.5 GB+ of memory**, even when only serving standard HTTP CRUD requests.
- **Vendor Fragmentation**: Maintaining separate SDKs and billing accounts for OpenAI, Anthropic, Google Gemini, and DeepSeek creates messy configuration and fragile code.
- **Lack of Rollback Safety in AI Workflows**: Multi-step AI agent pipelines (e.g. generating an article, creating social posts, uploading assets, updating the database) often fail halfway through, leaving dirty state in databases and caches.
- **Black-Box Asynchronous Execution**: Clients submitting long-running compute jobs are left polling database records with no real-time insight into progress or intermediate failures.

### The Solution
Muddy Server addresses these challenges through a purpose-built, dedicated computation tier:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             DOWNSTREAM CLIENTS                              │
│         (nischaysharma-server, Web Frontend, Background Daemons)            │
└───────────────────────┬─────────────────────────────▲───────────────────────┘
                        │ HTTP / REST                 │ WebSockets / SSE
                        ▼                             │ (0-100% Progress)
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MUDDY SERVER                                   │
│                                                                             │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌───────────────────┐  │
│  │ OpenRouter AI Gateway│  │ Transactional Runner │  │  Live WS Hub      │  │
│  │ (Claude/GPT/Gemini)  │  │ (Auto-Rollbacks)     │  │  (EventBus)       │  │
│  └──────────┬───────────┘  └──────────┬───────────┘  └─────────┬─────────┘  │
│             │                         │                        │            │
│  ┌──────────▼─────────────────────────▼────────────────────────▼──────────┐  │
│  │                     SQLAlchemy 2.0 Async Layer                         │  │
│  │           (compute_jobs, agent_sessions, pipeline_logs)                │  │
│  └────────────────────────────────────┬───────────────────────────────────┘  │
│                                       │                                     │
│  ┌────────────────────────────────────▼───────────────────────────────────┐  │
│  │                Feature-Flagged Providers (Zero RAM Waste)              │  │
│  │    [ProcessPool / Ray]    [Memory / Redis Queue]    [Statistical NLP]  │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ The Five Architectural Pillars

### 1. Centralized OpenRouter Gateway
- **One Unified Endpoint**: Directs all model inferences through `https://openrouter.ai/api/v1` using standard LangChain chat models.
- **One API Key**: Eliminates multiple billing dashboards; a single `OPENROUTER_API_KEY` provides access to **Claude 3.7 / 3.5 Sonnet**, **GPT-4o**, **Gemini 2.0 Flash / Pro**, and **DeepSeek R1**.
- **Automatic Model Resolution**: Translates concise short slugs (`claude-3.5-sonnet`, `gpt-4o`, `deepseek-r1`) into target provider slugs automatically.

### 2. Strict Zero-RAM / Zero-Process Overhead
- Subsystems are strictly guarded by feature flags in `.env`:
  - `ENABLE_ML_TRANSFORMERS=false` (Default)
  - `ENABLE_RAY_COMPUTE=false` (Default)
  - `ENABLE_REDIS_QUEUE=false` (Default)
- **Lazy Loading**: Heavy libraries like `torch`, `transformers`, and `ray` are never imported at the root level. In lightweight agent mode, Muddy Server operates with **< 60 MB of RAM**.

### 3. Transactional Pipelines with Reverse-Order Rollbacks
- Business and computation workflows are organized into discrete, atomic `BasePipelineStep` units.
- If Step 3 in a 4-step pipeline fails, Steps 2 and 1 are **automatically rolled back in reverse order**, restoring state and recording the error trace in SQL.

### 4. Real-Time Telemetry & WebSocket Channels
- Clients subscribe to room-based channels (`/api/v1/ws/jobs/{job_id}`).
- The internal `EventBus` captures state transitions, stage names, elapsed execution time, and weighted `0.0% - 100.0%` progress updates, broadcasting them instantly to connected WebSocket clients.

### 5. LangGraph Cyclic State Machines & Supervisors
- Goes beyond simple sequential prompts by supporting cyclic graphs (Planner ➔ Executor ➔ Reflector ➔ Synthesizer).
- Supervisor orchestrator dynamically decomposes complex goals and delegates work across specialized subagents (`researcher`, `coder`, `math_worker`).
