# Muddy Server 🚀

High-performance, modular Python AI Agent Backend powered by **FastAPI** and **LangGraph**.

## Features
- **Stateful Multi-Agent Orchestration**: Built on LangGraph with state graphs, conditional routing, and memory persistence.
- **Pluggable LLM Providers**: Unified interface supporting Google Gemini, OpenAI, Anthropic, and Local (Ollama) models.
- **Real-Time Streaming**: Server-Sent Events (SSE) and WebSocket endpoints streaming thought tokens, step actions, and tool outputs.
- **Model Context Protocol (MCP) & Tools**: Extensible tool registry with automatic schema reflection.
- **Persistence Checkpoints**: Session memory backed by in-memory or SQLite checkpointers.

## Getting Started

### Prerequisites
- Python >= 3.11 (Managed with `uv`)

### Installation
```bash
# In muddy-server directory:
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e .
```

### Configuration
Copy `.env.example` to `.env` and provide your API keys:
```bash
cp .env.example .env
```

### Running the Server
```bash
uv run uvicorn app.main:app --reload --port 8000
```
Interactive API docs will be available at [http://localhost:8000/docs](http://localhost:8000/docs).
