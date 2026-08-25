"""Async Database Session Management and Lifecycle."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config import settings
from app.core.logging import logger
from app.db.base import Base
# Ensure all models are imported so Base.metadata is populated
import app.db.models  # noqa: F401

# Engine initialization
engine_kwargs = {"echo": settings.DB_ECHO}
if "sqlite" not in settings.DATABASE_URL:
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
    })

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency providing an async database session per request."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def init_db() -> None:
    """Initializes tables in database schema."""
    logger.info(f"[DB] Initializing database schema on {settings.DATABASE_URL.split('?')[0]}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("[DB] Database schema initialized successfully.")


async def close_db() -> None:
    """Closes database connection pool on shutdown."""
    logger.info("[DB] Closing database engine pool.")
    await engine.dispose()
