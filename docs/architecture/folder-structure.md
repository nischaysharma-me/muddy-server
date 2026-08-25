# Architecture: Folder Structure 📂

Muddy Server maintains strict separation of concerns between API transport, business orchestration, low-level providers, database persistence, and pipelines.

```
muddy-server/
├── app/
│   ├── api/                     # REST & WebSocket API Routers
│   │   └── v1/
│   │       ├── endpoints/       # Route controllers (compute, agents, tools, ws, health, docs)
│   │       └── router.py        # Central v1 router aggregation
│   ├── config/                  # Modular Pydantic Settings
│   │   ├── ai.py                # LLM models, OpenRouter, aliases
│   │   ├── constants.py         # Enums (Environment, LLMProviderType, JobStatus)
│   │   ├── db.py                # SQL database & checkpointer configs
│   │   ├── features.py          # Strict feature flags controlling RAM & subsystems
│   │   ├── ray.py & redis.py    # Compute cluster & queue configs
│   │   └── server.py            # Host, Port, CORS, Environment
│   ├── core/                    # Core System Infrastructure
│   │   ├── event_bus.py         # Async Pub/Sub EventBus
│   │   ├── exceptions.py        # Custom domain exception hierarchy
│   │   ├── logging.py           # Structured Rich logging
│   │   └── security.py          # API key verification
│   ├── db/                      # SQLAlchemy 2.0 Async Layer
│   │   ├── base.py              # Declarative Base & UTC Timestamp/UUID mixins
│   │   ├── models/              # JobModel, AgentSessionModel, PipelineLogModel, ToolLogModel
│   │   └── session.py           # Async engine, session factory, get_db dependency
│   ├── memory/                  # Checkpointer & State Persistence
│   ├── pipelines/               # Transactional Pipeline Execution Engine
│   │   ├── base_step.py         # Base step contract (execute, rollback, validate)
│   │   ├── context.py           # Execution context, stage, telemetry
│   │   ├── middleware/          # Timing, retry, and validation middleware
│   │   ├── progress.py          # 0-100% weighted progress calculation
│   │   └── runner.py            # Pipeline runner with automated reverse rollback
│   ├── providers/               # Infrastructure & Algorithm Providers
│   │   ├── ai/                  # OpenRouter, Gemini, OpenAI, Claude, Mock providers
│   │   ├── compute/             # ProcessPool & lazy Ray distributed compute
│   │   ├── ml/                  # Statistical NLP, lazy HuggingFace embeddings & Cross-Encoders
│   │   ├── queues/              # In-memory async queue & Redis Arq
│   │   └── tools/               # Dynamic ToolRegistry & MCP Client Bridge
│   ├── schemas/                 # Pydantic Request & Response DTOs
│   ├── services/                # High-Level Orchestration Services
│   │   ├── agent_service.py     # Agent chat, workflows, supervisor coordination
│   │   ├── docs_service.py      # Markdown catalog and documentation tree
│   │   ├── job_service.py       # Background compute job lifecycle
│   │   ├── llm_service.py       # Multi-model LLM generation and streaming
│   │   ├── nlp_service.py       # Embeddings, candidate reranking, similarity
│   │   └── tool_service.py      # Dynamic tool execution and audit logging
│   ├── websockets/              # Live WebSocket Hub & Broadcaster
│   │   ├── broadcaster.py       # EventBus to WebSocket bridge
│   │   ├── connection_manager.py# Channel room connection tracker
│   │   └── handlers.py          # Handshake and heartbeat ping/pong
│   └── main.py                  # FastAPI application entrypoint & lifespan
├── docs/                        # Comprehensive Markdown Documentation
├── tests/                       # Pytest Test Suite
│   ├── integration/             # End-to-end API integration tests
│   └── unit/                    # Unit tests per subsystem
├── pyproject.toml               # Project packaging specification
└── requirements.txt             # Unpinned dependencies list
```
