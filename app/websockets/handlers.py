"""WebSocket Message and Frame Handlers."""

from typing import Any, Dict
from fastapi import WebSocket, WebSocketDisconnect
from app.core.logging import logger
from app.websockets.connection_manager import connection_manager


async def handle_websocket_session(websocket: WebSocket, channel_id: str):
    """Handles the lifecycle loop of a connected WebSocket client."""
    await connection_manager.connect(websocket, channel_id)
    try:
        # Send initial confirmation frame
        await websocket.send_json({
            "event": "connected",
            "channel_id": channel_id,
            "status": "ready",
        })

        while True:
            # Listen for client frames (e.g. heartbeat ping)
            data = await websocket.receive_json()
            msg_type = data.get("type", "ping")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong", "channel_id": channel_id})

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, channel_id)
    except Exception as e:
        logger.warning(f"[WS] Connection error on channel '{channel_id}': {e}")
        connection_manager.disconnect(websocket, channel_id)
