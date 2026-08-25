# Guide: Getting Started 🚀

Step-by-step instructions to get Muddy Server up and running locally.

---

## 1. Virtual Environment & Dependencies
```bash
# In muddy-server root:
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e .
```

---

## 2. Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Provide your OpenRouter API Key:
```env
DEFAULT_LLM_PROVIDER="openrouter"
OPENROUTER_API_KEY="sk-or-v1-..."
```

---

## 3. Starting the Server
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser to inspect interactive OpenAPI documentation.
