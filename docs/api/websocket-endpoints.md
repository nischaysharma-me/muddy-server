# API Reference: WebSocket Endpoints 📡

Real-time bi-directional streaming endpoints for job progress and agent thought telemetry.

---

### `WS /api/v1/ws/jobs/{job_id}`
Connects a client to a real-time progress channel for a specific compute job.
- **Connection Handshake**:
  Client receives:
  ```json
  {
    "event": "connected",
    "channel_id": "job-123",
    "status": "ready"
  }
  ```
- **Live Progress Frames**:
  ```json
  {
    "event": "job.progress",
    "data": {
      "job_id": "job-123",
      "stage": "TRANSFORMER_EMBEDDING_STAGE",
      "progress_pct": 60.0,
      "elapsed_ms": 230.5
    }
  }
  ```
- **Ping / Heartbeat**:
  Send `{"type": "ping"}` -> Receive `{"type": "pong", "channel_id": "job-123"}`.

---

### `WS /api/v1/ws/agents/{session_id}`
Streams live reasoning thoughts, tool calls, and step tokens for an active agent conversation thread.
