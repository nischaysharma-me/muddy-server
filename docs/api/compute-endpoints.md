# API Reference: Compute Endpoints ⚡

Endpoints for submitting background compute jobs, text candidate reranking, and direct LLM generation.

---

### `POST /api/v1/compute/jobs`
Submits an asynchronous compute job to the background queue.
- **Request Body**:
  ```json
  {
    "job_type": "article_generation",
    "payload": {
      "topic": "Microservices with LangGraph",
      "model": "anthropic/claude-3.5-sonnet"
    },
    "run_async": true
  }
  ```
- **Response** (`202 Accepted`):
  ```json
  {
    "job_id": "4a71b2d0-7a0b-47e2-8874-325d2334812a",
    "status": "queued",
    "ws_stream_url": "/api/v1/ws/jobs/4a71b2d0-7a0b-47e2-8874-325d2334812a",
    "message": "Compute job accepted and queued successfully."
  }
  ```

---

### `GET /api/v1/compute/jobs/{job_id}`
Retrieves latest execution status, 0–100% progress, and JSON result.
- **Response** (`200 OK`):
  ```json
  {
    "job_id": "4a71b2d0-7a0b-47e2-8874-325d2334812a",
    "status": "completed",
    "progress": 100.0,
    "stage": "COMPLETED",
    "result": { "article": "# Microservices with LangGraph..." },
    "execution_time_ms": 1420.5
  }
  ```

---

### `DELETE /api/v1/compute/jobs/{job_id}`
Cancels a pending or running compute job.

---

### `POST /api/v1/compute/nlp/rerank`
Reranks documents by query relevance.
- **Request Body**:
  ```json
  {
    "query": "FastAPI async database",
    "documents": ["PostgreSQL and SQLAlchemy 2.0 Async", "Cooking recipes"],
    "top_k": 5
  }
  ```

---

### `POST /api/v1/compute/llm/generate`
Direct text completion via OpenRouter.
- **Request Body**:
  ```json
  {
    "prompt": "Write a high-performance database schema",
    "model": "claude-3.5-sonnet",
    "temperature": 0.7
  }
  ```
