"""Real-Time WebSocket Endpoints for Job Progress and Agent Telemetry."""

from fastapi import APIRouter, WebSocket
from app.config import settings
from app.core.exceptions import FeatureDisabledError
from app.websockets.handlers import handle_websocket_session

router = APIRouter(prefix="/ws", tags=["WebSockets & Live Telemetry"])


@router.websocket("/jobs/{job_id}")
async def job_progress_ws(websocket: WebSocket, job_id: str):
    """Real-time WebSocket stream emitting live 0–100% progress and stage events for a specific job."""
    if not settings.ENABLE_WEBSOCKETS:
        await websocket.close(code=1008, reason="WebSockets are disabled in server configuration")
        return
    await handle_websocket_session(websocket, channel_id=job_id)


@router.websocket("/agents/{session_id}")
async def agent_telemetry_ws(websocket: WebSocket, session_id: str):
    """Real-time WebSocket stream emitting live agent reasoning thoughts, tool calls, and step tokens."""
    if not settings.ENABLE_WEBSOCKETS:
        await websocket.close(code=1008, reason="WebSockets are disabled in server configuration")
        return
    await handle_websocket_session(websocket, channel_id=session_id)
