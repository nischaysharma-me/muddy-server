"""System Info Diagnostic Tool."""

import platform
import sys
from datetime import datetime, timezone
from typing import Dict, Any
from app.tools.registry import registry


@registry.register(
    name="get_system_status",
    description="Retrieves the current runtime environment diagnostics, OS information, Python version, and UTC timestamp.",
    category="system",
)
def get_system_status() -> Dict[str, Any]:
    """Returns runtime system diagnostics."""
    return {
        "status": "online",
        "current_time_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "server_engine": "FastAPI + LangGraph (Muddy Server)",
    }
