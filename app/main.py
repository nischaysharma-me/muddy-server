"""FastAPI Main Entrypoint for Muddy Server."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
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

    @application.get("/documentation", response_class=HTMLResponse, tags=["Documentation Portal"])
    async def documentation_portal():
        from app.services.docs_service import docs_service
        tree = docs_service.get_documentation_tree()
        nav_html = ""
        for section in tree:
            nav_html += f"<div class='section-title'>{section['title']}</div><ul class='doc-list'>"
            for f in section['files']:
                nav_html += f"<li><a href='javascript:void(0)' onclick=\"loadDoc('{section['section']}', '{f['name']}')\">{f['title']}</a></li>"
            nav_html += "</ul>"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{settings.APP_NAME} - Documentation Portal</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        :root {{ --bg: #0d1117; --sidebar: #161b22; --text: #c9d1d9; --accent: #58a6ff; --border: #30363d; }}
        body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); display: flex; height: 100vh; }}
        #sidebar {{ width: 280px; background: var(--sidebar); border-right: 1px solid var(--border); overflow-y: auto; padding: 20px 15px; box-sizing: border-box; }}
        #sidebar h2 {{ font-size: 1.1rem; color: #fff; margin-top: 0; display: flex; align-items: center; gap: 8px; }}
        .section-title {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #8b949e; margin: 16px 0 6px 8px; font-weight: 600; }}
        .doc-list {{ list-style: none; padding: 0; margin: 0; }}
        .doc-list li a {{ display: block; padding: 6px 10px; color: var(--text); text-decoration: none; border-radius: 6px; font-size: 0.9rem; transition: background 0.15s; }}
        .doc-list li a:hover, .doc-list li a.active {{ background: #21262d; color: var(--accent); }}
        #content {{ flex: 1; overflow-y: auto; padding: 40px 60px; max-width: 900px; line-height: 1.6; box-sizing: border-box; }}
        pre {{ background: #161b22; border: 1px solid var(--border); border-radius: 8px; padding: 16px; overflow-x: auto; }}
        code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 0.85em; }}
        h1, h2, h3 {{ color: #f0f6fc; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
        a {{ color: var(--accent); }}
        table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
        th, td {{ border: 1px solid var(--border); padding: 8px 12px; text-align: left; }}
        th {{ background: #161b22; color: #f0f6fc; }}
    </style>
</head>
<body>
    <div id="sidebar">
        <h2>🚀 {settings.APP_NAME} Docs</h2>
        <div style="font-size: 0.8rem; color: #8b949e; margin-bottom: 15px;"><a href="/docs" style="color: var(--accent);">Interactive OpenAPI /docs ↗</a></div>
        {nav_html}
    </div>
    <div id="content">
        <div id="doc-body">Select a topic from the sidebar to view documentation.</div>
    </div>
    <script>
        async function loadDoc(section, name) {{
            document.querySelectorAll('.doc-list li a').forEach(el => el.classList.remove('active'));
            event && event.target && event.target.classList.add('active');
            const res = await fetch(`/api/v1/docs/${{section}}/${{name}}`);
            if (res.ok) {{
                const data = await res.json();
                document.getElementById('doc-body').innerHTML = marked.parse(data.content);
                hljs.highlightAll();
            }}
        }}
        // Load first document by default
        window.onload = () => {{
            const first = document.querySelector('.doc-list li a');
            if (first) first.click();
        }};
    </script>
</body>
</html>"""

    @application.get("/", tags=["Root"])
    async def root():
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "documentation_portal": "/documentation",
            "health": "/api/v1/health",
        }

    return application


app = create_app()
