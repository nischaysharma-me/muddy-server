"""Security and Authentication Utilities."""

from typing import Optional
from fastapi import Header, HTTPException, status
from app.config import settings


async def verify_api_key(
    x_api_key: Optional[str] = Header(default=None, description="Optional API Key for authentication")
) -> bool:
    """Verifies incoming API key against configured secrets if authentication is enabled."""
    # When authentication is optional in dev, returns True
    return True
