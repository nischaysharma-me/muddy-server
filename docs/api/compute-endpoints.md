# API Reference: Compute Endpoints ⚡

Complete specification for asynchronous job submissions, candidate reranking, text similarity scoring, and direct LLM generation.

---

## 1. `POST /api/v1/compute/jobs`
Submits a computation job to the background queue. Returns an immediate `< 5ms` acknowledgment with a unique `job_id` and WebSocket telemetry URL.

### Request Body
```json
{
  "job_type": "article_generation",
  "payload": {
    "topic": "Microservices with LangGraph",
    "target_audience": "Senior Software Engineers",
    "generate_images": true
  },
  "run_async": true
}
```

### Response (`202 Accepted`)
```json
{
  "job_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "queued",
  "ws_stream_url": "/api/v1/ws/jobs/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "message": "Compute job accepted and queued successfully."
}
```

### cURL Example
```bash
curl -X POST "http://localhost:8000/api/v1/compute/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "job_type": "heavy_computation",
    "payload": { "iterations": 500 }
  }'
```

---

## 2. `GET /api/v1/compute/jobs/{job_id}`
Polls the execution status, progress, stage, execution duration, and JSON results of a specific compute job.

### Path Parameters
- `job_id` (*string, required*): The UUID returned upon job submission.

### Response (`200 OK`)
```json
{
  "job_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "completed",
  "progress": 100.0,
  "stage": "COMPLETED",
  "job_type": "article_generation",
  "result": {
    "title": "Microservices with LangGraph",
    "markdown_content": "# Architecture Overview...",
    "tags": ["python", "langgraph", "fastapi"]
  },
  "error": null,
  "execution_time_ms": 1240.5,
  "created_at": "2026-08-25T16:00:00Z",
  "updated_at": "2026-08-25T16:00:01Z"
}
```

---

## 3. `DELETE /api/v1/compute/jobs/{job_id}`
Cancels an active or queued compute job and marks its state as `cancelled` in the database.

### Response (`200 OK`)
```json
{
  "job_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "cancelled": true
}
```

---

## 4. `POST /api/v1/compute/nlp/rerank`
Reranks candidate document passages against a search query using lexical/statistical TF-IDF scoring (or Cross-Encoders when ML is enabled).

### Request Body
```json
{
  "query": "FastAPI async database connection pooling",
  "documents": [
    "Astrophysics and stellar formation theories",
    "PostgreSQL connection pooling with asyncpg and SQLAlchemy 2.0",
    "Plant biology and botanical gardens"
  ],
  "top_k": 2
}
```

### Response (`200 OK`)
```json
{
  "query": "FastAPI async database connection pooling",
  "results": [
    {
      "index": 1,
      "score": 0.8421,
      "document": "PostgreSQL connection pooling with asyncpg and SQLAlchemy 2.0"
    }
  ]
}
```

---

## 5. `POST /api/v1/compute/nlp/similarity`
Computes lexical cosine similarity between two text passages on a `0.0` to `1.0` scale.

### Request Body
```json
{
  "text_a": "FastAPI Python async backend framework",
  "text_b": "FastAPI and Python high performance async server"
}
```

### Response (`200 OK`)
```json
{
  "similarity_score": 0.7746
}
```

---

## 6. `POST /api/v1/compute/llm/generate`
Executes single-turn text completion via OpenRouter or direct provider.

### Request Body
```json
{
  "prompt": "Summarize the benefits of event-driven microservices in 3 bullets",
  "provider": "openrouter",
  "model": "claude-3.5-sonnet",
  "temperature": 0.5
}
```

### Response (`200 OK`)
```json
{
  "provider": "openrouter",
  "model": "claude-3.5-sonnet",
  "content": "1. Decoupled Service Architecture...\n2. High Scalability...\n3. Fault Tolerance..."
}
```

---

## 7. `POST /api/v1/compute/llm/stream`
Streams generated model tokens in real-time as **Server-Sent Events (SSE)**.

### Response Stream Protocol
```
event: delta
data: Decoupled

event: delta
data:  Service

event: delta
data:  Architecture

event: done
data: [DONE]
```
