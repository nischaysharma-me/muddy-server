"""WebSocket Broadcaster bridging EventBus events to active socket clients."""

from typing import Any, Dict
from app.core.event_bus import event_bus
from app.core.logging import logger
from app.websockets.connection_manager import connection_manager


class WebSocketBroadcaster:
    """Listens to internal EventBus events and forwards them in real-time to WebSocket clients."""

    def __init__(self):
        self._is_initialized = False

    def initialize(self) -> None:
        """Registers global EventBus subscribers."""
        if self._is_initialized:
            return

        event_bus.subscribe("job.started", self._handle_job_event)
        event_bus.subscribe("job.progress", self._handle_job_event)
        event_bus.subscribe("job.completed", self._handle_job_event)
        event_bus.subscribe("job.failed", self._handle_job_event)
        event_bus.subscribe("agent.event", self._handle_agent_event)

        self._is_initialized = True
        logger.info("[WS] WebSocketBroadcaster initialized and listening to EventBus.")

    async def _handle_job_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        job_id = payload.get("job_id")
        if not job_id:
            return

        message = {
            "event": event_type,
            "data": payload,
        }
        # Broadcast to channel room matching job_id
        await connection_manager.broadcast_to_channel(job_id, message)

    async def _handle_agent_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        session_id = payload.get("session_id")
        if not session_id:
            return

        message = {
            "event": event_type,
            "data": payload,
        }
        await connection_manager.broadcast_to_channel(session_id, message)


# Global WebSocket Broadcaster Singleton
ws_broadcaster = WebSocketBroadcaster()
