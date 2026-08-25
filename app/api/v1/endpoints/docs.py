"""Documentation API Endpoints for Programmatic Markdown Retrieval and Navigation."""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from app.services.docs_service import docs_service

router = APIRouter(prefix="/docs", tags=["Documentation Engine"])


@router.get("/tree", response_model=List[Dict[str, Any]])
async def get_docs_navigation_tree():
    """Returns the full hierarchical navigation tree of all documentation files."""
    return docs_service.get_documentation_tree()


@router.get("/{section}/{doc_name}", response_model=Dict[str, Any])
async def get_documentation_page(section: str, doc_name: str):
    """Retrieves markdown content for a specific documentation page."""
    doc = docs_service.get_document(section, doc_name)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Documentation page '{section}/{doc_name}' not found.")
    return doc


@router.get("/{section}/{doc_name}/raw", response_class=PlainTextResponse)
async def get_raw_markdown_page(section: str, doc_name: str):
    """Returns raw markdown text for a specific documentation page."""
    doc = docs_service.get_document(section, doc_name)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Documentation page '{section}/{doc_name}' not found.")
    return doc["content"]
