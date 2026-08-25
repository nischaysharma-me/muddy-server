"""Global Constants and Enums."""

from enum import Enum


class Environment(str, Enum):
    """Application runtime environment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LLMProviderType(str, Enum):
    """Supported LLM providers."""
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    MOCK = "mock"


class JobStatus(str, Enum):
    """Lifecycle status of a compute job."""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ErrorCode(str, Enum):
    """Standardized error codes."""
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    FEATURE_DISABLED = "FEATURE_DISABLED"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    PIPELINE_ERROR = "PIPELINE_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"
