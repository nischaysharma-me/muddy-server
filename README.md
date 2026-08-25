# Muddy Server 🚀

**Muddy Server** is a modular, zero-hardcoding **Computation-as-a-Service (CaaS)** backend engine built with **FastAPI**, **SQLAlchemy 2.0 Async**, **LangGraph**, and **OpenRouter**.

It serves as the dedicated compute and AI provider for downstream applications (such as `nischaysharma-server` and web clients) with real-time WebSocket progress telemetry, transactional pipeline execution with automatic rollbacks, and strict feature-flagged RAM isolation.

---

## 🌟 Architectural Highlights

### 1. 🌐 Centralized OpenRouter Gateway & Multi-Model AI
- **Unified Multi-Model Gateway**: Access **Claude 3.7 / 3.5 Sonnet, GPT-4o / o3, Gemini 2.0 Flash / Pro, DeepSeek R1 / V3, Llama 3.3 70B, Qwen, and Mistral** via a single OpenRouter endpoint.
- Standard short aliases (`gpt-4o`, `claude-3.5-sonnet`, `gemini-2.0-flash`, `deepseek-r1`) resolve automatically.
- Direct provider fallbacks (`gemini`, `openai`, `anthropic`, `local`, `mock`).

### 2. 🗄️ Async SQL Database & Transactions
- **SQLAlchemy 2.0 Async** ORM with SQLite (local development) and PostgreSQL (production).
- Declarative models:
  - `JobModel` (`compute_jobs`): Tracks background jobs, 0–100% progress, stage transitions, JSONB payloads, and results.
  - `AgentSessionModel` (`agent_sessions`): Stores persistent conversation history and memory snapshots.
  - `PipelineLogModel` (`pipeline_logs`): Step-by-step transaction logs with execution timings.
  - `ToolLogModel` (`tool_audit_logs`): Comprehensive audit trail of every tool and MCP call.

### 3. 🔄 Transactional Pipeline Engine
- **Lifecycle Hooks**: Automatic validation before each step, timing middleware, and exponential retry.
- **Rollback Safety**: If any step in a pipeline fails, previous steps are automatically rolled back in reverse order.
- **Progress Tracking**: Emits weighted 0–100% progress events across the internal `EventBus`.

### 4. ⚡ Real-Time WebSocket Hub & Event Broadcaster
- Channel room subscriptions (`/api/v1/ws/jobs/{job_id}` and `/api/v1/ws/agents/{session_id}`).
- Automatic JSON frame broadcasting on job state changes and live agent reasoning tokens.

### 5. ⚙️ Compute & Multiprocessing Providers (Zero RAM Waste)
- **Feature Flags**: Subsystems are toggled via `.env` (`ENABLE_ML_TRANSFORMERS=false`, `ENABLE_RAY_COMPUTE=false`, `ENABLE_REDIS_QUEUE=false`).
- **ProcessPoolComputeEngine**: Default lightweight process/thread executor with zero background memory overhead.
- **Ray Distributed Actor Engine**: Cluster compute initialized lazily only when enabled.

### 6. 📥 Distributed Async Job Queues
- **MemoryQueue**: Default in-memory async worker queue returning `< 5ms` instant job IDs.
- **RedisArqQueue**: Distributed Redis worker queue for high-throughput production loads.

### 7. 🧠 LangGraph Cyclic State Graphs & Multi-Agent Supervisors
- ReAct conversational agents with dynamic tool execution.
- Cyclic State Graph DAG (Planner ➔ Executor ➔ Reflector ➔ Synthesizer).
- Supervisor orchestrator coordinating specialized subagents (`researcher`, `coder`, `math_worker`).

### 8. 🔍 Machine Learning & Statistical NLP
- Zero-dependency regex tokenizer, TF-IDF cosine similarity, and lexical candidate reranker.
- Local Transformer dense embeddings and Cross-Encoder neural rerankers (lazy-loaded when enabled).

---

## 🛠️ API Overview

| Method | Path | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/compute/jobs` | Submits a compute job to background queue |
| `GET` | `/api/v1/compute/jobs/{id}` | Retrieves live status, stage, 0-100% progress, and results |
| `DELETE` | `/api/v1/compute/jobs/{id}` | Cancels a queued or executing job |
| `WS` | `/api/v1/ws/jobs/{id}` | Real-time WebSocket stream for job progress telemetry |
| `WS` | `/api/v1/ws/agents/{id}` | Real-time WebSocket stream for agent reasoning thoughts |
| `POST` | `/api/v1/compute/nlp/rerank` | Reranks candidate documents based on query relevance |
| `POST` | `/api/v1/compute/nlp/similarity` | Calculates lexical similarity score between two texts |
| `POST` | `/api/v1/compute/llm/generate` | Direct multi-model LLM completion via OpenRouter |
| `POST` | `/api/v1/compute/llm/stream` | Server-Sent Events (SSE) token stream |
| `POST` | `/api/v1/agents/chat` | Executes conversational ReAct agent with tools & memory |
| `POST` | `/api/v1/agents/workflow/run` | Executes LangGraph cyclic state graph DAG |
| `POST` | `/api/v1/agents/supervisor/run` | Executes multi-agent supervisor team |

---

## 🚀 Quick Start

### 1. Prerequisites
- Python >= 3.11 (Recommended: Python 3.12 managed with `uv`)

### 2. Installation
```bash
# In muddy-server directory:
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e .
```

### 3. Environment Setup
```bash
cp .env.example .env
```
Configure your OpenRouter API key in `.env`:
```env
DEFAULT_LLM_PROVIDER="openrouter"
OPENROUTER_API_KEY="sk-or-v1-..."
```

### 4. Running the Server
```bash
uv run uvicorn app.main:app --reload --port 8000
```
Interactive OpenAPI documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

### 5. Running the Test Suite
```bash
uv run pytest -v
```
All **50 unit and integration tests** execute in ~2 seconds.
