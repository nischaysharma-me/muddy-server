# Architecture: Service Pattern ⚙️

## 1. Overview & Separation of Concerns

Muddy Server strictly separates HTTP routing from business logic:
- **API Controllers (`app/api/`)**: Focus exclusively on endpoint routing, request validation via Pydantic schemas, HTTP status codes, and serialization.
- **Service Layer (`app/services/`)**: Encapsulates orchestration, database transactions, background queue coordination, event emission, and error handling.

Services are instantiated as singletons and exported for consumption by API endpoints and background workers.

---

## 2. Core Service Catalog

```
                                  ┌────────────────────────┐
                                  │     FastAPI Router     │
                                  └───────────┬────────────┘
                                              │
         ┌──────────────────┬─────────────────┼──────────────────┬──────────────────┐
         ▼                  ▼                 ▼                  ▼                  ▼
    JobService         AgentService       LLMService         ToolService        NLPService
  - Async Queues     - ReAct Chat       - OpenRouter       - ToolRegistry     - Lexical Tokenizer
  - SQL Status Sync  - Cyclic Workflows - Token Streaming  - MCP Bridge       - Reranker
  - Telemetry Events - Memory Snapshots - Prompt Formatting- Audit Logs       - Similarity
```

---

## 3. Service Deep Dives

### `JobService` ([`app/services/job_service.py`](file:///Users/davinci/Documents/sscorp/nischaysharma.com/muddy-server/app/services/job_service.py))
- **Responsibilities**:
  - Accepts compute requests and generates UUID job IDs in `< 5ms`.
  - Creates the initial `JobModel` record with status `queued`.
  - Dispatches work to `MemoryQueue` or `RedisArqQueue`.
  - Emits lifecycle events (`job.queued`, `job.started`, `job.progress`, `job.completed`, `job.failed`).
  - Supports non-blocking job cancellation.

### `AgentService` ([`app/services/agent_service.py`](file:///Users/davinci/Documents/sscorp/nischaysharma.com/muddy-server/app/services/agent_service.py))
- **Responsibilities**:
  - Orchestrates single/multi-turn conversational ReAct agent execution.
  - Runs cyclic LangGraph DAGs (Planner ➔ Executor ➔ Reflector ➔ Synthesizer).
  - Coordinates multi-agent supervisor teams delegating subtasks to worker agents.
  - Automatically serializes conversation snapshots to SQL `AgentSessionModel`.

### `LLMService` ([`app/services/llm_service.py`](file:///Users/davinci/Documents/sscorp/nischaysharma.com/muddy-server/app/services/llm_service.py))
- **Responsibilities**:
  - Unified multi-model text completion interface.
  - Asynchronous token streaming iterator for Server-Sent Events (SSE).

### `ToolService` ([`app/services/tool_service.py`](file:///Users/davinci/Documents/sscorp/nischaysharma.com/muddy-server/app/services/tool_service.py))
- **Responsibilities**:
  - Manages catalog of registered Python tools and external MCP server tools.
  - Executes tools dynamically with type coercion.
  - Automatically records execution duration and audit logs into SQL `ToolLogModel`.

### `NLPService` ([`app/services/nlp_service.py`](file:///Users/davinci/Documents/sscorp/nischaysharma.com/muddy-server/app/services/nlp_service.py))
- **Responsibilities**:
  - Zero-overhead regex tokenization and stopword removal.
  - Cosine lexical similarity scoring between text pairs.
  - Query-document candidate reranking.
