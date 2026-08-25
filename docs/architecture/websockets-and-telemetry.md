# Architecture: WebSockets & Real-Time Telemetry ⚡

Muddy Server bridges internal events to external clients in real-time over WebSocket channel rooms and Server-Sent Events (SSE).

---

## 📡 Components

### 1. Connection Manager (`ConnectionManager`)
- Manages active client sockets keyed by room channel (`job_id` or `session_id`).
- Supports broadcast to channel and broadcast to all connected clients.
- Cleanly handles sudden disconnects and connection cleanups.

### 2. EventBus Bridge (`WebSocketBroadcaster`)
- Automatically subscribes to `event_bus` channels:
  - `job.started`, `job.progress`, `job.completed`, `job.failed`
  - `agent.event`
- Formats payloads into structured JSON frames and forwards them to the matching channel room.

### 3. Client Frame Format
```json
{
  "event": "job.progress",
  "data": {
    "job_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "stage": "PROCESSING_PAYLOAD",
    "progress_pct": 75.0,
    "elapsed_ms": 142.5
  }
}
```
