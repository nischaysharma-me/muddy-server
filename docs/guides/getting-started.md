# Guide: Getting Started 🚀

This guide walks you through setting up, configuring, and running **Muddy Server** from scratch.

---

## 1. Prerequisites
- **Python >= 3.12**
- **uv** (Recommended: install via `curl -LsSf https://astral.sh/uv/install.sh | sh` or `brew install uv`)
- **OpenRouter API Key** (Get one at [openrouter.ai/keys](https://openrouter.ai/keys))

---

## 2. Step-by-Step Installation

### Step A: Clone & Create Virtual Environment
```bash
# Navigate to muddy-server directory
cd /path/to/muddy-server

# Create virtual environment with Python 3.12
uv venv --python 3.12 .venv
source .venv/bin/activate
```

### Step B: Install Dependencies
```bash
uv pip install -e .
```

### Step C: Environment Configuration
Copy the template configuration:
```bash
cp .env.example .env
```

Edit `.env` and set your OpenRouter API key:
```env
# Server
APP_NAME="Muddy Server"
ENVIRONMENT="development"
DEBUG=true
PORT=8000

# OpenRouter Configuration (Unified Multi-Model Gateway)
DEFAULT_LLM_PROVIDER="openrouter"
OPENROUTER_API_KEY="sk-or-v1-your-api-key-here"
OPENROUTER_MODEL="google/gemini-2.0-flash-001"
OPENROUTER_SITE_URL="https://nischaysharma.com"
OPENROUTER_APP_NAME="Muddy Server"

# Database (SQLite by default)
DATABASE_URL="sqlite+aiosqlite:///muddy_server.db"

# Subsystems
ENABLE_LLM_GATEWAY=true
ENABLE_AGENTS=true
ENABLE_WEBSOCKETS=true
ENABLE_SQL_DB=true
ENABLE_DOCS_ENGINE=true

# Heavy Compute Flags (Keep false for lightweight zero-RAM operation)
ENABLE_ML_TRANSFORMERS=false
ENABLE_RAY_COMPUTE=false
ENABLE_REDIS_QUEUE=false
```

---

## 3. Running the Application

Start the development server with live reload:
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see startup logs in your terminal:
```
INFO:     🚀 Starting Muddy Server v0.1.0
INFO:     🔧 Environment: development | Debug: True
INFO:     🧠 Default LLM Provider: openrouter
INFO:     [DB] Initializing database schema on sqlite+aiosqlite:///muddy_server.db
INFO:     [DB] Database schema initialized successfully.
INFO:     [WS] WebSocketBroadcaster initialized and listening to EventBus.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 4. Exploring the Endpoints

| Portal | URL | Description |
| :--- | :--- | :--- |
| **Interactive Docs Portal** | [http://localhost:8000/documentation](http://localhost:8000/documentation) | Full structured documentation reader with sidebar |
| **Swagger / OpenAPI** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive API exploration and testing UI |
| **ReDoc UI** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | Alternate OpenAPI documentation reader |
| **Health Check** | [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health) | System uptime, version, and provider status |

---

## 5. Running the Test Suite
Ensure everything is configured and passing:
```bash
uv run pytest -v
```
All **54 tests** should pass in ~2 seconds.
