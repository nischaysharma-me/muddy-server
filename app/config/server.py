"""Server and Network Configuration Settings."""

from typing import List
from pydantic import Field
from app.config.base import BaseSettings
from app.config.constants import Environment


class ServerSettings(BaseSettings):
    """Core server network, host, port, and CORS settings."""

    APP_NAME: str = Field(default="Muddy Server", description="Name of the application")
    APP_VERSION: str = Field(default="0.1.0", description="Semantic version")
    ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT, description="Runtime environment")
    DEBUG: bool = Field(default=True, description="Debug mode")
    HOST: str = Field(default="0.0.0.0", description="Binding host")
    PORT: int = Field(default=8000, description="Listening port")

    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ],
        description="Allowed CORS origin domains",
    )
