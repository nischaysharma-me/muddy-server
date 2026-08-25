# Architecture: Service Pattern ⚙️

The **Service Layer** in Muddy Server orchestrates business logic, database persistence, pub/sub telemetry, and provider invocation. Controllers (endpoints) remain thin and delegate all execution to dedicated services.

---

## Service Catalog (`app/services/`)

### 1. `JobService`
- Coordinates asynchronous computation jobs.
- Enqueues work into `MemoryQueue` or `RedisArqQueue`.
- Creates and updates `JobModel` records in SQL.
- Emits `job.queued`, `job.started`, `job.progress`, `job.completed`, and `job.failed` across the `EventBus`.

### 2. `LLMService`
- Manages single-turn and streaming text generation across models.
- Interacts with `OpenRouterLLMProvider` and direct providers.

### 3. `ToolService`
- Aggregates internal tools registered in `ToolRegistry` and external tools discovered via `MCPClientBridge`.
- Logs every invocation into SQL `ToolLogModel` for compliance, latency auditing, and error tracking.

### 4. `AgentService`
- Coordinates single-turn chat, Server-Sent Events (SSE) streaming, LangGraph cyclic state graphs, and Multi-Agent Supervisors.
- Automatically saves state snapshots into SQL `AgentSessionModel`.

### 5. `NLPService`
- Provides lexical tokenization, text similarity calculation, document reranking, and semantic embedding generation.
