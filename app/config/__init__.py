"""Central Configuration Package for Muddy Server."""

from app.config.ai import AISettings
from app.config.constants import Environment, ErrorCode, JobStatus, LLMProviderType
from app.config.db import DatabaseSettings
from app.config.features import FeatureSettings
from app.config.ray import RaySettings
from app.config.redis import RedisSettings
from app.config.server import ServerSettings


class Settings(
    ServerSettings,
    FeatureSettings,
    AISettings,
    DatabaseSettings,
    RaySettings,
    RedisSettings,
):
    """Unified application settings combining all modular configuration sections."""

    pass


# Global Typed Settings Singleton
settings = Settings()

__all__ = [
    "settings",
    "Settings",
    "Environment",
    "LLMProviderType",
    "JobStatus",
    "ErrorCode",
]
