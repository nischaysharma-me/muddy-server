# Postman Collection & Environment Guide 📮

Muddy Server includes a ready-to-import **Postman Collection (v2.1)** and **Environment JSON** covering all REST endpoints, streaming APIs, agent execution workflows, and the **Tool Marketplace**.

---

## 📁 Postman Files Location

- **Postman Collection**: [`docs/api/postman/muddy_server_collection.json`](file:///Users/davinci/Documents/sscorp/nischaysharma.com/muddy-server/docs/api/postman/muddy_server_collection.json)
- **Postman Environment**: [`docs/api/postman/muddy_server_environment.json`](file:///Users/davinci/Documents/sscorp/nischaysharma.com/muddy-server/docs/api/postman/muddy_server_environment.json)

---

## 🚀 How to Import into Postman

1. Open **Postman** (or Insomnia / Bruno / Thunder Client in VSCode).
2. Click the **Import** button in the top left.
3. Drag & drop or browse to:
   - `docs/api/postman/muddy_server_collection.json`
   - `docs/api/postman/muddy_server_environment.json`
4. In the top right environment dropdown, select **`Muddy Server - Local`**.

---

## 📋 Included Request Groups

| Folder | Request Name | Method | Path | Description |
| :--- | :--- | :---: | :--- | :--- |
| **Health & System** | Root Information | `GET` | `/` | Server metadata & portals |
| | Health Check | `GET` | `/api/v1/health` | System health, uptime & status |
| | Documentation Portal | `GET` | `/documentation` | Interactive HTML markdown explorer |
| **Compute & Jobs** | Submit Compute Job | `POST` | `/api/v1/compute/jobs` | Enqueues async compute job (sets `{{job_id}}` automatically) |
| | Get Compute Job Status | `GET` | `/api/v1/compute/jobs/{{job_id}}` | Real-time status, 0-100% progress & outputs |
| | Cancel Compute Job | `DELETE` | `/api/v1/compute/jobs/{{job_id}}` | Cancels queued or running job |
| | Document Reranker | `POST` | `/api/v1/compute/nlp/rerank` | Reranks candidate passages by query relevance |
| | Text Similarity | `POST` | `/api/v1/compute/nlp/similarity` | Cosine similarity score |
| | Direct LLM Completion | `POST` | `/api/v1/compute/llm/generate` | Text generation via OpenRouter |
| | Direct LLM Stream (SSE) | `POST` | `/api/v1/compute/llm/stream` | Real-time Server-Sent Events stream |
| **AI Agents** | Conversational Chat | `POST` | `/api/v1/agents/chat` | ReAct agent with dynamic tool execution |
| | Conversational Stream | `POST` | `/api/v1/agents/chat/stream` | Real-time agent thought streaming |
| | LangGraph State Graph | `POST` | `/api/v1/agents/workflow/run` | Cyclic DAG (Planner ➔ Executor ➔ Reflector) |
| | Multi-Agent Supervisor | `POST` | `/api/v1/agents/supervisor/run` | Supervisor delegating across subagents |
| **Tools & MCP** | List All Tools | `GET` | `/api/v1/tools` | Discovers internal tools & MCP tools |
| | Execute Tool | `POST` | `/api/v1/tools/calculator/execute` | Executes tool directly & logs to SQL |
| | List MCP Servers | `GET` | `/api/v1/tools/mcp/servers` | Discovers connected MCP tool servers |
| **Tool Marketplace** | Browse Catalog | `GET` | `/api/v1/tools/marketplace` | Lists discovered tools with category & search filters |
| | Get Tool Detail | `GET` | `/api/v1/tools/marketplace/{{tool_id}}` | Views schema, README & code preview |
| | Scaffold Tool | `POST` | `/api/v1/tools/marketplace/scaffold` | Creates starter boilerplate files on disk |
| | Upload Custom Tool | `POST` | `/api/v1/tools/marketplace/upload` | Uploads and registers new tool bundle |
| | Install / Enable Tool | `POST` | `/api/v1/tools/marketplace/{{tool_id}}/install` | Enables tool for live agents |
| | Uninstall / Disable Tool | `POST` | `/api/v1/tools/marketplace/{{tool_id}}/uninstall` | Disables tool dynamically |
| | Delete Custom Tool | `DELETE` | `/api/v1/tools/marketplace/{{tool_id}}` | Permanently deletes custom tool folder |
| **Docs Engine** | Get Docs Tree | `GET` | `/api/v1/docs/tree` | Hierarchical documentation tree |
| | Get Doc Page | `GET` | `/api/v1/docs/{section}/{name}` | Structured markdown and metadata |
| | Get Raw Markdown | `GET` | `/api/v1/docs/{section}/{name}/raw` | Plain text markdown |

---

## ⚡ Environment Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `{{base_url}}` | `http://localhost:8000` | HTTP root endpoint of Muddy Server |
| `{{ws_base_url}}` | `ws://localhost:8000` | WebSocket root endpoint |
| `{{provider}}` | `openrouter` | Default LLM provider |
| `{{model}}` | `gemini-3.7-flash` | Active frontier model |
| `{{job_id}}` | *(Auto-set)* | Automatically populated upon calling *Submit Compute Job* |
| `{{session_id}}` | `session-test-001` | Active conversation session identifier |
| `{{tool_id}}` | `currency_converter` | Active marketplace tool identifier |
