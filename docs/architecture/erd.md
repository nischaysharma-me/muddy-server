# Architecture: Database Entity Relationship Diagram (ERD) 📊

Muddy Server uses **SQLAlchemy 2.0 Async** ORM for non-blocking database I/O. It supports SQLite (`aiosqlite`) for local development/testing and PostgreSQL (`asyncpg`) for production.

---

## 🏗️ Entity Relationship Diagram

```
┌──────────────────────────────────────┐          ┌──────────────────────────────────────┐
│             compute_jobs             │          │            pipeline_logs             │
├──────────────────────────────────────┤          ├──────────────────────────────────────┤
│ id (PK, UUID)                        │◄───┐     │ id (PK, UUID)                        │
│ status (queued/processing/completed) │    └─────┼ job_id (FK/Ref, UUID)                │
│ progress (Float, 0.0 - 100.0)        │          │ pipeline_name (String)               │
│ stage (String, e.g. STEP_1)          │          │ step_name (String)                   │
│ job_type (String)                    │          │ status (SUCCESS/FAILED/ROLLED_BACK)  │
│ payload (JSON / JSONB)               │          │ duration_ms (Float)                  │
│ result (JSON / JSONB)                │          │ step_details (JSON / JSONB)          │
│ error (Text)                         │          │ error_message (Text)                 │
│ execution_time_ms (Float)            │          │ created_at (DateTime, UTC)           │
│ created_at (DateTime, UTC)           │          └──────────────────────────────────────┘
│ updated_at (DateTime, UTC)           │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐          ┌──────────────────────────────────────┐
│            agent_sessions            │          │           tool_audit_logs            │
├──────────────────────────────────────┤          ├──────────────────────────────────────┤
│ id (PK, UUID)                        │          │ id (PK, UUID)                        │
│ session_id (Unique String)           │◄─────────┼ session_id (FK/Ref, String)          │
│ agent_type (conversational/workflow) │          │ tool_name (String)                   │
│ provider (openrouter/gemini/mock)    │          │ is_mcp (Boolean)                     │
│ model (claude-3.5-sonnet/gpt-4o)     │          │ arguments (JSON / JSONB)             │
│ state_snapshot (JSON / JSONB)        │          │ result (JSON / JSONB)                │
│ session_metadata (JSON / JSONB)      │          │ is_error (Boolean)                   │
│ created_at (DateTime, UTC)           │          │ error_message (Text)                 │
│ updated_at (DateTime, UTC)           │          │ duration_ms (Float)                  │
└──────────────────────────────────────┘          │ created_at (DateTime, UTC)           │
                                                  └──────────────────────────────────────┘
```

---

## 📑 Field-by-Field Table Dictionary

### 1. `compute_jobs` (`JobModel`)
| Field | Type | Modifiers | Description |
| :--- | :--- | :--- | :--- |
| `id` | String(36) | Primary Key, UUID | Unique identifier generated upon submission |
| `status` | String(32) | Indexed | Current state: `queued`, `processing`, `completed`, `failed`, `cancelled` |
| `progress` | Float | Default: 0.0 | Weighted progress percentage (`0.0` to `100.0`) |
| `stage` | String(64) | - | Human-readable stage name (e.g. `TRANSFORMER_ENCODING`, `COMPLETED`) |
| `job_type` | String(64) | Indexed | Classification identifier (e.g. `article_generation`, `math_sim`) |
| `trace_id` | String(64) | Indexed | Distributed tracing identifier |
| `payload` | JSON / JSONB | - | Input parameters submitted by client |
| `result` | JSON / JSONB | - | Final output produced upon successful completion |
| `error` | Text | Nullable | Stack trace and error diagnostic if execution failed |
| `execution_time_ms`| Float | Nullable | Total execution duration in milliseconds |
| `created_at` | DateTime | Indexed, UTC | Timestamp when job was enqueued |
| `updated_at` | DateTime | UTC | Timestamp of last status or progress update |

---

### 2. `agent_sessions` (`AgentSessionModel`)
| Field | Type | Modifiers | Description |
| :--- | :--- | :--- | :--- |
| `id` | String(36) | Primary Key, UUID | Internal primary key |
| `session_id` | String(128) | Unique, Indexed | Client conversation thread identifier |
| `agent_type` | String(64) | Indexed | `conversational`, `workflow_graph`, or `supervisor` |
| `provider` | String(64) | - | AI Provider used (e.g. `openrouter`) |
| `model` | String(128) | - | Active model slug (e.g. `claude-3.5-sonnet`) |
| `state_snapshot`| JSON / JSONB| - | Serialized LangGraph state, message history, plan |
| `session_metadata`| JSON / JSONB| - | Additional client context or user session metadata |

---

### 3. `pipeline_logs` (`PipelineLogModel`)
| Field | Type | Modifiers | Description |
| :--- | :--- | :--- | :--- |
| `id` | String(36) | Primary Key, UUID | Step log UUID |
| `job_id` | String(36) | Indexed | Associated compute job UUID |
| `pipeline_name`| String(128)| Indexed | Name of pipeline runner |
| `step_name` | String(128)| - | Name of individual step |
| `status` | String(32) | - | `SUCCESS`, `FAILED`, or `ROLLED_BACK` |
| `duration_ms` | Float | - | Elapsed step execution time |
| `step_details` | JSON / JSONB| - | Intermediate inputs and outputs |
| `error_message`| Text | Nullable | Step-level failure reason |

---

### 4. `tool_audit_logs` (`ToolLogModel`)
| Field | Type | Modifiers | Description |
| :--- | :--- | :--- | :--- |
| `id` | String(36) | Primary Key, UUID | Audit record UUID |
| `session_id` | String(128)| Indexed | Associated conversation session |
| `tool_name` | String(128)| Indexed | Function name of tool invoked |
| `is_mcp` | Boolean | Default: False | True if invoked via external MCP server |
| `arguments` | JSON / JSONB| - | Parameters passed to tool |
| `result` | JSON / JSONB| - | Output returned by tool |
| `is_error` | Boolean | Default: False | True if tool execution raised exception |
| `duration_ms` | Float | - | Tool execution latency in ms |
