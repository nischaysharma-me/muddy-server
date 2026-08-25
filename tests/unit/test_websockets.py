"""Unit tests for WebSocket Endpoints, Connection Manager, and Event Broadcasting."""

import asyncio
import pytest
from starlette.testclient import TestClient
from app.core.event_bus import event_bus
from app.main import app
from app.websockets import connection_manager, ws_broadcaster


@pytest.fixture(autouse=True)
def init_broadcaster():
    ws_broadcaster.initialize()


def test_websocket_job_connection_and_ping():
    client = TestClient(app)
    job_id = "test-job-ws-123"

    with client.websocket_connect(f"/api/v1/ws/jobs/{job_id}") as websocket:
        # Initial connected frame
        initial_frame = websocket.receive_json()
        assert initial_frame["event"] == "connected"
        assert initial_frame["channel_id"] == job_id
        assert initial_frame["status"] == "ready"

        # Ping frame
        websocket.send_json({"type": "ping"})
        pong_frame = websocket.receive_json()
        assert pong_frame["type"] == "pong"
        assert pong_frame["channel_id"] == job_id


def test_websocket_live_event_broadcast():
    client = TestClient(app)
    job_id = "test-broadcast-job-456"

    with client.websocket_connect(f"/api/v1/ws/jobs/{job_id}") as websocket:
        # Consume initial connected frame
        _ = websocket.receive_json()

        # Emit an event on event_bus in an event loop
        async def trigger_event():
            await event_bus.emit("job.progress", {
                "job_id": job_id,
                "stage": "RAY_COMPUTE_STAGE",
                "progress_pct": 75.0,
                "elapsed_ms": 150.2,
            })

        asyncio.run(trigger_event())

        # Receive broadcasted message on WebSocket
        frame = websocket.receive_json()
        assert frame["event"] == "job.progress"
        assert frame["data"]["job_id"] == job_id
        assert frame["data"]["progress_pct"] == 75.0
        assert frame["data"]["stage"] == "RAY_COMPUTE_STAGE"
