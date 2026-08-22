"""Health and System Status Diagnostic Endpoint."""

import sys
import platform
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/health", tags=["Health & Diagnostics"])


@router.get("", summary="System Health Check")
async def health_check() -> Dict[str, Any]:
    """Returns the operational status, environment configuration, and active LLM providers."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "runtime": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "architecture": platform.machine(),
        },
        "llm": {
            "default_provider": settings.DEFAULT_LLM_PROVIDER,
            "gemini_configured": bool(settings.GEMINI_API_KEY),
            "openai_configured": bool(settings.OPENAI_API_KEY),
            "anthropic_configured": bool(settings.ANTHROPIC_API_KEY),
        },
        "persistence": {
            "checkpointer": settings.CHECKPOINTER_TYPE,
        },
    }
