"""WebSocket Connection Registry and Channel Room Manager."""

from collections import defaultdict
from typing import Dict, List, Set
from fastapi import WebSocket
from app.core.logging import logger


class ConnectionManager:
    """Manages active WebSocket connections grouped into channel rooms (e.g. per job_id or session_id)."""

    def __init__(self):
        # channel_id -> set of active WebSockets
        self._channels: Dict[str, Set[WebSocket]] = defaultdict(set)
        self._all_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, channel_id: str) -> None:
        """Accepts a WebSocket connection and registers it to a specific channel room."""
        await websocket.accept()
        self._channels[channel_id].add(websocket)
        self._all_connections.add(websocket)
        logger.debug(f"[WS] Client connected to channel '{channel_id}' (Total in room: {len(self._channels[channel_id])})")

    def disconnect(self, websocket: WebSocket, channel_id: str) -> None:
        """Removes a WebSocket connection on client disconnect."""
        if websocket in self._channels[channel_id]:
            self._channels[channel_id].remove(websocket)
            if not self._channels[channel_id]:
                del self._channels[channel_id]
        if websocket in self._all_connections:
            self._all_connections.remove(websocket)
        logger.debug(f"[WS] Client disconnected from channel '{channel_id}'")

    async def broadcast_to_channel(self, channel_id: str, message: dict) -> None:
        """Broadcasts a JSON message payload to all sockets in a specific channel."""
        sockets = list(self._channels.get(channel_id, []))
        if not sockets:
            return

        dead_sockets = []
        for ws in sockets:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning(f"[WS] Failed sending to socket in channel '{channel_id}': {e}")
                dead_sockets.append(ws)

        for dead_ws in dead_sockets:
            self.disconnect(dead_ws, channel_id)

    async def broadcast_all(self, message: dict) -> None:
        """Broadcasts a message to all connected clients across all channels."""
        sockets = list(self._all_connections)
        for ws in sockets:
            try:
                await ws.send_json(message)
            except Exception:
                pass

    def get_channel_count(self, channel_id: str) -> int:
        """Returns count of active clients in a channel."""
        return len(self._channels.get(channel_id, set()))


# Global Connection Manager Singleton
connection_manager = ConnectionManager()
