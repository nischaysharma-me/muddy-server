# Architecture: Database Entity Relationship Diagram (ERD) 📊

Muddy Server uses **SQLAlchemy 2.0 Async** ORM with support for SQLite (dev/test) and PostgreSQL (production).

---

## 🏗️ Tables Schema

### 1. `compute_jobs` (`JobModel`)
Stores state, progress, stage, input payload, and JSON results for background jobs.
- `id` (String[36], Primary Key, UUID)
- `status` (String[32], Indexed: `queued`, `processing`, `completed`, `failed`, `cancelled`)
- `progress` (Float, `0.0` to `100.0`)
- `stage` (String[64], e.g. `INITIALIZING`, `PROCESSING_PAYLOAD`, `COMPLETED`)
- `job_type` (String[64], Indexed)
- `trace_id` (String[64], Indexed)
- `payload` (JSON / JSONB)
- `result` (JSON / JSONB)
- `error` (Text)
- `execution_time_ms` (Float)
- `created_at` (DateTime, UTC, Indexed)
- `updated_at` (DateTime, UTC)

### 2. `agent_sessions` (`AgentSessionModel`)
Stores conversational thread snapshots, active models, and LangGraph state.
- `id` (String[36], Primary Key, UUID)
- `session_id` (String[128], Unique, Indexed)
- `agent_type` (String[64], Indexed: `conversational`, `workflow_graph`, `supervisor`)
- `provider` (String[64])
- `model` (String[128])
- `state_snapshot` (JSON / JSONB)
- `session_metadata` (JSON / JSONB)
- `created_at` (DateTime, UTC)
- `updated_at` (DateTime, UTC)

### 3. `pipeline_logs` (`PipelineLogModel`)
Tracks step-by-step telemetry, intermediate durations, and rollback logs.
- `id` (String[36], Primary Key, UUID)
- `job_id` (String[36], Indexed)
- `pipeline_name` (String[128], Indexed)
- `step_name` (String[128])
- `status` (String[32]: `SUCCESS`, `FAILED`, `ROLLED_BACK`)
- `duration_ms` (Float)
- `step_details` (JSON / JSONB)
- `error_message` (Text)
- `created_at` (DateTime, UTC)

### 4. `tool_audit_logs` (`ToolLogModel`)
Audit log recording every execution of internal tools and external MCP server tools.
- `id` (String[36], Primary Key, UUID)
- `session_id` (String[128], Indexed)
- `tool_name` (String[128], Indexed)
- `is_mcp` (Boolean)
- `arguments` (JSON / JSONB)
- `result` (JSON / JSONB)
- `is_error` (Boolean)
- `error_message` (Text)
- `duration_ms` (Float)
- `created_at` (DateTime, UTC)
