"""Custom Exception Classes for Muddy Server."""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class MuddyServerException(Exception):
    """Base exception for all domain errors in Muddy Server."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AgentExecutionError(MuddyServerException):
    """Raised when an agent fails during execution or reasoning cycle."""
    pass


class ToolExecutionError(MuddyServerException):
    """Raised when an agent tool fails to execute."""
    pass


class ModelProviderError(MuddyServerException):
    """Raised when an LLM provider fails (e.g. missing API key, rate limits)."""
    pass


class AgentHTTPException(HTTPException):
    """HTTP Exception tailored for Agent errors."""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "An agent error occurred",
        error_code: str = "AGENT_ERROR",
        extra: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={"error": detail, "code": error_code, "extra": extra or {}},
        )
