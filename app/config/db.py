"""SQL Database and Persistence Configuration."""

from pydantic import Field
from app.config.base import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database connection and pool settings supporting SQLite and PostgreSQL."""

    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///muddy_server.db",
        description="Async database connection string (e.g. sqlite+aiosqlite:/// or postgresql+asyncpg://)",
    )
    DB_ECHO: bool = Field(default=False, description="Log raw SQL queries")
    DB_POOL_SIZE: int = Field(default=10, description="Connection pool size for PostgreSQL")
    DB_MAX_OVERFLOW: int = Field(default=20, description="Max overflow connections")
    CHECKPOINTER_TYPE: str = Field(default="sqlite", description="Checkpointer type (sqlite, memory, postgres)")
    CHECKPOINTER_DB_PATH: str = Field(default="agent_checkpoints.db", description="SQLite checkpoint path")
