# API Reference: Agent Endpoints 🤖

Endpoints for Conversational ReAct agents, cyclic workflow graphs, and multi-agent supervisors.

---

### `POST /api/v1/agents/chat`
Executes single-turn or multi-turn conversational agent chat with memory and dynamic tool execution.
- **Request Body**:
  ```json
  {
    "message": "Calculate (128 * 45) + 12 and search for latest LangGraph updates",
    "provider": "openrouter",
    "model": "claude-3.5-sonnet",
    "session_id": "thread-123",
    "temperature": 0.7
  }
  ```

---

### `POST /api/v1/agents/chat/stream`
Streams conversational agent reasoning thoughts, tool calls, and response tokens via Server-Sent Events (SSE).

---

### `POST /api/v1/agents/workflow/run`
Runs the LangGraph Cyclic State Graph (Planner ➔ Executor ➔ Reflector ➔ Synthesizer).
- **Request Body**:
  ```json
  {
    "goal": "Conduct complete architectural review and performance analysis",
    "max_steps": 4
  }
  ```

---

### `POST /api/v1/agents/supervisor/run`
Coordinates multi-agent supervisor team delegating subtasks across specialized subagents (`researcher`, `coder`, `math_worker`).
- **Request Body**:
  ```json
  {
    "task": "Build an authenticated API endpoint with full test coverage"
  }
  ```
