# Architecture: Directory & Folder Structure 📂

This document provides a comprehensive, file-by-file roadmap of the **Muddy Server** codebase.

---

## 🌳 Full Directory Layout

```
muddy-server/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── agents.py           # Conversational, cyclic DAG, supervisor endpoints
│   │       │   ├── compute.py          # Asynchronous jobs, candidate rerank, LLM generate
│   │       │   ├── docs.py             # Programmatic markdown documentation endpoints
│   │       │   ├── health.py           # Health checks and uptime monitoring
│   │       │   ├── tools.py            # Dynamic tool catalog and execution endpoint
│   │       │   └── ws.py               # WebSocket telemetry streams (/ws/jobs, /ws/agents)
│   │       └── router.py               # Master API v1 Router aggregator
│   │
│   ├── config/
│   │   ├── ai.py                       # Model aliases, OpenRouter endpoint, temperature
│   │   ├── constants.py                # Enums (Environment, LLMProviderType, JobStatus)
│   │   ├── db.py                       # Database connection strings & checkpointer paths
│   │   ├── features.py                 # Strict feature flags controlling RAM & subsystems
│   │   ├── ray.py                      # Ray cluster address & resource configs
│   │   ├── redis.py                    # Redis host, port, db configs
│   │   └── server.py                   # App name, host, port, CORS, environment
│   │
│   ├── core/
│   │   ├── event_bus.py                # In-memory async Pub/Sub event bus
│   │   ├── exceptions.py               # Domain exception hierarchy (FeatureDisabledError, etc.)
│   │   ├── logging.py                  # Structured Rich logging formatter
│   │   └── security.py                 # API Key authentication dependency
│   │
│   ├── db/
│   │   ├── base.py                     # Declarative Base & UTC Timestamp/UUID mixins
│   │   ├── session.py                  # Async SQLAlchemy engine, sessionmaker, init_db()
│   │   └── models/
│   │       ├── agent_session.py        # AgentSessionModel (agent_sessions table)
│   │       ├── job.py                  # JobModel (compute_jobs table)
│   │       ├── pipeline_log.py         # PipelineLogModel (pipeline_logs table)
│   │       └── tool_log.py             # ToolLogModel (tool_audit_logs table)
│   │
│   ├── memory/
│   │   └── checkpointer.py             # LangGraph checkpointer initialization
│   │
│   ├── pipelines/
│   │   ├── base_step.py                # BasePipelineStep contract (validate, execute, rollback)
│   │   ├── context.py                  # PipelineContext shared state container
│   │   ├── progress.py                 # Weighted 0-100% progress calculator
│   │   ├── runner.py                   # PipelineRunner with automated reverse rollback
│   │   └── middleware/
│   │       ├── retry.py                # Retry middleware with exponential backoff
│   │       └── timing.py               # Microsecond step latency measurement
│   │
│   ├── providers/
│   │   ├── ai/                         # LLM Providers (OpenRouter, Gemini, OpenAI, Claude, Mock)
│   │   ├── compute/                    # Compute Engines (ProcessPool, Ray)
│   │   ├── ml/                         # NLP & Embeddings (Statistical NLP, Cross-Encoders)
│   │   ├── queues/                     # Async Queues (MemoryQueue, RedisArqQueue)
│   │   └── tools/                      # ToolRegistry & Model Context Protocol (MCP) Bridge
│   │
│   ├── schemas/                        # Pydantic Request & Response DTOs
│   │   ├── agents.py                   # Agent chat & workflow schemas
│   │   ├── compute.py                  # Job submission, reranking, LLM generation schemas
│   │   └── tools.py                    # Tool description and execution schemas
│   │
│   ├── services/                       # Central Orchestration Layer
│   │   ├── agent_service.py            # Agent chat & multi-agent supervisor workflows
│   │   ├── docs_service.py             # Markdown documentation indexer and parser
│   │   ├── job_service.py              # Background compute job queue & SQL coordinator
│   │   ├── llm_service.py              # Direct text completion and SSE token streamer
│   │   ├── nlp_service.py              # Statistical similarity and document reranker
│   │   └── tool_service.py             # Dynamic tool runner & SQL audit logger
│   │
│   ├── websockets/
│   │   ├── broadcaster.py              # EventBus to WebSocket bridge
│   │   ├── connection_manager.py       # Room-based WebSocket connection manager
│   │   └── handlers.py                 # Ping/Pong heartbeat and frame handlers
│   │
│   └── main.py                         # FastAPI application factory, lifespan, and UI portal
│
├── docs/                               # Production-Grade Markdown Documentation
│   ├── about/                          # Application overview, developer conventions
│   ├── api/                            # REST & WebSocket endpoint specifications
│   ├── architecture/                   # Architecture, ERD, OpenRouter, and Pipelines
│   └── guides/                         # Setup, custom tools, pipelines, and RAM optimization
│
├── tests/
│   ├── integration/                    # End-to-end HTTP and WebSocket API tests
│   └── unit/                           # Subsystem-isolated unit tests
│
├── pyproject.toml                      # Project metadata and dependency configuration
└── requirements.txt                    # Unpinned package list
```

---

## 🔄 Dependency Flow Rules

To maintain long-term maintainability:
1. **API Endpoints** may depend only on **Schemas** and **Services**.
2. **Services** may depend on **Providers**, **Database Models**, and **Core**.
3. **Providers** must remain completely decoupled and interact only through abstract interfaces.
4. **Database Models** must contain no business logic.
