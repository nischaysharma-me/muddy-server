# API Reference: Agent Endpoints 🤖

Endpoints for Conversational ReAct agents, LangGraph cyclic state graphs, and Multi-Agent Supervisors.

---

## 1. `POST /api/v1/agents/chat`
Executes single-turn or multi-turn conversational ReAct agent with persistent memory checkpoints and dynamic tool execution.

### Request Body
```json
{
  "message": "Calculate (45 * 12) + 18 and tell me what operating system this server is running on.",
  "provider": "openrouter",
  "model": "claude-3.5-sonnet",
  "session_id": "thread-user-1234",
  "tools": ["calculator", "get_system_status", "web_search"],
  "temperature": 0.7
}
```

### Response (`200 OK`)
```json
{
  "session_id": "thread-user-1234",
  "response": "The calculation result is 558. The server is currently running on Darwin (macOS).",
  "agent_type": "conversational",
  "provider": "openrouter",
  "model": "claude-3.5-sonnet",
  "steps": [
    {
      "step_number": 1,
      "step_type": "tool_call",
      "content": "Calling tool 'calculator' with args {'expression': '(45 * 12) + 18'}"
    },
    {
      "step_number": 2,
      "step_type": "tool_result",
      "content": "Tool 'calculator' returned: 558"
    },
    {
      "step_number": 3,
      "step_type": "tool_call",
      "content": "Calling tool 'get_system_status' with args {}"
    },
    {
      "step_number": 4,
      "step_type": "tool_result",
      "content": "Tool 'get_system_status' returned: {'status': 'healthy', 'platform': 'Darwin'}"
    }
  ],
  "tool_calls": [
    {
      "id": "call_1",
      "name": "calculator",
      "arguments": { "expression": "(45 * 12) + 18" }
    }
  ],
  "execution_time_ms": 842.15,
  "created_at": "2026-08-25T16:10:00Z"
}
```

---

## 2. `POST /api/v1/agents/chat/stream`
Streams live thoughts, step events, tool calls, and text tokens as **Server-Sent Events (SSE)**.

### Stream Event Types:
- `event: init` -> Initializes conversation session.
- `event: tool_call` -> Emitted when the agent decides to invoke an external tool.
- `event: tool_result` -> Emitted when tool execution completes.
- `event: delta` -> Live text chunk from the LLM.
- `event: final` -> Stream completion marker.

---

## 3. `POST /api/v1/agents/workflow/run`
Executes the LangGraph Cyclic State Graph (Planner ➔ Executor ➔ Reflector ➔ Synthesizer).

### Request Body
```json
{
  "goal": "Analyze distributed database replication lag strategies",
  "max_steps": 4,
  "session_id": "workflow-run-90"
}
```

### Response (`200 OK`)
```json
{
  "session_id": "workflow-run-90",
  "goal": "Analyze distributed database replication lag strategies",
  "plan": [
    "1. Analyze context and available tools",
    "2. Query domain knowledge or run system diagnostics",
    "3. Synthesize and formulate comprehensive output"
  ],
  "observations": [
    "Step 1 executed. System observation: Status=healthy, Platform=Darwin"
  ],
  "final_output": "### Workflow Execution Summary\n**Goal**: Analyze distributed database...",
  "steps_executed": 3,
  "is_completed": true
}
```

---

## 4. `POST /api/v1/agents/supervisor/run`
Coordinates a team of specialized subagents (`researcher`, `coder`, `math_worker`) managed by a supervisor planner.

### Request Body
```json
{
  "task": "Build an authenticated rate-limited API endpoint with full pytest test coverage",
  "session_id": "supervisor-sess-1"
}
```

### Response (`200 OK`)
```json
{
  "session_id": "supervisor-sess-1",
  "response": "### Supervisor Orchestration Result\n\n**Task**: Build an authenticated rate-limited API...\n\n**Subagent Findings**:\n- **Research Agent**: Gathered rate-limiting algorithms (Token Bucket, Leaky Bucket).\n- **Coding Agent**: Drafted FastAPI dependency decorator with Redis sliding window.",
  "agent_type": "supervisor",
  "provider": "supervisor-orchestrator",
  "model": "multi-agent-team",
  "steps": [
    {
      "step_number": 1,
      "step_type": "plan",
      "content": "Supervisor analyzing task and delegating subtasks"
    }
  ],
  "execution_time_ms": 1120.4
}
```
