"""Domain Exception Hierarchy and HTTP Exception Wrappers."""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from app.config.constants import ErrorCode


class MuddyException(Exception):
    """Base exception for all domain errors in Muddy Server."""

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class ConfigurationError(MuddyException):
    """Raised when configuration or environment parameters are invalid."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=ErrorCode.CONFIGURATION_ERROR, details=details)


class FeatureDisabledError(MuddyException):
    """Raised when an operation is requested on a disabled feature flag."""

    def __init__(self, feature_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Feature '{feature_name}' is currently disabled in configuration.",
            code=ErrorCode.FEATURE_DISABLED,
            details=details or {"feature": feature_name},
        )


class ModelProviderError(MuddyException):
    """Raised when an external or local LLM provider fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=ErrorCode.PROVIDER_ERROR, details=details)


class PipelineExecutionError(MuddyException):
    """Raised when a transactional pipeline step fails during execution."""

    def __init__(self, message: str, step_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        extra = details or {}
        if step_name:
            extra["failed_step"] = step_name
        super().__init__(message, code=ErrorCode.PIPELINE_ERROR, details=extra)


class ToolExecutionError(MuddyException):
    """Raised when a registered agent tool fails."""

    def __init__(self, message: str, tool_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        extra = details or {}
        if tool_name:
            extra["tool_name"] = tool_name
        super().__init__(message, code=ErrorCode.PROVIDER_ERROR, details=extra)


# Backwards compatible alias
AgentExecutionError = PipelineExecutionError
MuddyServerException = MuddyException


class MuddyHTTPException(HTTPException):
    """Structured HTTP Exception returned across all API endpoints."""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "A compute engine error occurred",
        code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        extra: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error": detail,
                "code": code.value if isinstance(code, ErrorCode) else code,
                "extra": extra or {},
            },
        )


AgentHTTPException = MuddyHTTPException
