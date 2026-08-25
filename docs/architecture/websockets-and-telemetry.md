# Architecture: WebSockets & Real-Time Telemetry ⚡

## 1. Overview

Long-running compute jobs (e.g. multi-step article generation, dense vector clustering, or multi-agent workflows) can take anywhere from **1 to 30+ seconds**. Polling HTTP REST endpoints (`GET /jobs/{id}`) causes unnecessary server load and poor UX.

Muddy Server integrates a native **WebSocket Hub** and **EventBus Bridge** enabling real-time streaming of:
- **0.0% to 100.0% weighted progress updates**.
- **Active execution stage transitions** (e.g. `STEP_1_FETCH`, `STEP_2_SUMMARIZE`, `COMPLETED`).
- **Agent reasoning tokens and intermediate tool execution results**.

---

## 2. Telemetry Architecture

```
┌───────────────────────────┐
│     Pipeline / Service    │
└─────────────┬─────────────┘
              │ 1. Emits event (e.g. 'job.progress')
              ▼
┌───────────────────────────┐
│     Async EventBus        │  (app/core/event_bus.py)
└─────────────┬─────────────┘
              │ 2. Dispatches to registered subscribers
              ▼
┌───────────────────────────┐
│   WebSocketBroadcaster    │  (app/websockets/broadcaster.py)
└─────────────┬─────────────┘
              │ 3. Finds room for 'channel_id' (job_id / session_id)
              ▼
┌───────────────────────────┐
│    ConnectionManager      │  (app/websockets/connection_manager.py)
└─────────────┬─────────────┘
              │ 4. Broadcasts JSON frame to all active client sockets in room
              ▼
┌───────────────────────────┐
│      WebSocket Client     │
└───────────────────────────┘
```

---

## 3. WebSocket Channel Endpoints

### 1. Job Progress Stream: `WS /api/v1/ws/jobs/{job_id}`
Connects to the progress telemetry channel for a specific background compute job.

### 2. Agent Telemetry Stream: `WS /api/v1/ws/agents/{session_id}`
Connects to the real-time reasoning stream for an agent conversation thread.

---

## 4. Message Protocol Specification

### Handshake Response (`connected`)
Sent immediately by the server upon successful connection:
```json
{
  "event": "connected",
  "channel_id": "8b51d7e2-411a-4c28-98bc-21a4f001192e",
  "status": "ready"
}
```

### Live Progress Update (`job.progress`)
Broadcasted whenever a pipeline step finishes or progress changes:
```json
{
  "event": "job.progress",
  "data": {
    "job_id": "8b51d7e2-411a-4c28-98bc-21a4f001192e",
    "pipeline_name": "article_generation",
    "stage": "STEP_2_GENERATE_SUMMARY",
    "progress_pct": 66.7,
    "elapsed_ms": 342.1,
    "status": "PROCESSING"
  }
}
```

### Final Completion Frame (`job.completed`)
```json
{
  "event": "job.completed",
  "data": {
    "job_id": "8b51d7e2-411a-4c28-98bc-21a4f001192e",
    "pipeline_name": "article_generation",
    "progress_pct": 100.0,
    "elapsed_ms": 520.4,
    "outputs": {
      "article_title": "Modern AI Architecture with LangGraph",
      "summary": "..."
    }
  }
}
```

### Heartbeat (Ping/Pong)
- **Client Frame**: `{"type": "ping"}`
- **Server Frame**: `{"type": "pong", "channel_id": "8b51d7e2-..."}`

---

## 5. Client Integration Code Example (JavaScript / TypeScript)

```javascript
// 1. Submit Job via REST
const submitRes = await fetch("http://localhost:8000/api/v1/compute/jobs", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    job_type: "article_simulation",
    payload: { prompt: "Distributed Systems in 2026" }
  })
});
const { job_id, ws_stream_url } = await submitRes.json();

// 2. Connect to WebSocket Stream
const ws = new WebSocket(`ws://localhost:8000${ws_stream_url}`);

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  
  if (msg.event === "job.progress") {
    console.log(`[Progress]: ${msg.data.progress_pct}% - Stage: ${msg.data.stage}`);
    updateProgressBar(msg.data.progress_pct);
  } else if (msg.event === "job.completed") {
    console.log("[Completed!]:", msg.data.outputs);
    ws.close();
  }
};
```
