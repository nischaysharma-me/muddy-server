"""FastAPI Main Entrypoint for Muddy Server."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import MuddyServerException
from app.core.logging import logger
# Ensure custom tools are imported and registered
import app.tools.custom  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan event handler."""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"🔧 Environment: {settings.ENVIRONMENT} | Debug: {settings.DEBUG}")
    logger.info(f"🧠 Default LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")

    if settings.ENABLE_SQL_DB:
        from app.db.session import init_db, close_db
        try:
            await init_db()
        except Exception as e:
            logger.error(f"[DB] Database initialization error: {e}")

    if settings.ENABLE_WEBSOCKETS:
        from app.websockets import ws_broadcaster
        ws_broadcaster.initialize()

    yield

    if settings.ENABLE_SQL_DB:
        from app.db.session import close_db
        try:
            await close_db()
        except Exception as e:
            logger.error(f"[DB] Error closing database: {e}")

    logger.info(f"🛑 Shutting down {settings.APP_NAME}")


def create_app() -> FastAPI:
    """Factory function to build and configure FastAPI application."""
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="High-performance, modular Python AI Agent Backend powered by FastAPI and LangGraph",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Domain Exception Handlers
    @application.exception_handler(MuddyServerException)
    async def muddy_exception_handler(request: Request, exc: MuddyServerException):
        return JSONResponse(
            status_code=500,
            content={"error": exc.message, "details": exc.details},
        )

    # Mount API Routers
    application.include_router(api_router, prefix="/api/v1")

    @application.get("/", tags=["Root"])
    async def root():
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/api/v1/health",
        }

    return application


app = create_app()
