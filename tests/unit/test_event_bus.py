"""Unit tests for EventBus asynchronous event dispatcher."""

import pytest
from app.core.event_bus import EventBus


@pytest.mark.asyncio
async def test_event_bus_subscribe_and_emit():
    bus = EventBus()
    received_events = []

    async def sample_handler(event_type: str, payload: dict):
        received_events.append((event_type, payload))

    bus.subscribe("job.progress", sample_handler)
    await bus.emit("job.progress", {"job_id": "123", "progress": 50.0})

    assert len(received_events) == 1
    assert received_events[0][0] == "job.progress"
    assert received_events[0][1]["progress"] == 50.0


@pytest.mark.asyncio
async def test_event_bus_global_subscriber():
    bus = EventBus()
    received_events = []

    async def global_handler(event_type: str, payload: dict):
        received_events.append(event_type)

    bus.subscribe_all(global_handler)
    await bus.emit("job.started", {})
    await bus.emit("job.completed", {})

    assert len(received_events) == 2
    assert "job.started" in received_events
    assert "job.completed" in received_events
