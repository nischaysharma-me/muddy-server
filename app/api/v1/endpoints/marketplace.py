"""Tool Marketplace REST Endpoints."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.marketplace import (
    MarketplaceToolDetailResponse,
    MarketplaceToolItem,
    ToolActionResponse,
    ToolScaffoldRequest,
    ToolScaffoldResponse,
    ToolUploadRequest,
)
from app.services.tool_marketplace_service import tool_marketplace_service

router = APIRouter(prefix="/tools/marketplace", tags=["Tool Marketplace & Plugins"])


@router.get("", response_model=List[MarketplaceToolItem], summary="Browse Marketplace Tools")
async def browse_marketplace_tools(
    category: Optional[str] = Query(default=None, description="Filter by category (finance, developer, nlp, web)"),
    tag: Optional[str] = Query(default=None, description="Filter by tag"),
    search: Optional[str] = Query(default=None, description="Search query across tool name, description, tags"),
):
    """Returns a catalog of all discovered marketplace tools with filter and search capabilities."""
    return tool_marketplace_service.list_marketplace_tools(
        category=category, tag=tag, search=search
    )


@router.get("/{tool_id}", response_model=MarketplaceToolDetailResponse, summary="Get Marketplace Tool Detail")
async def get_tool_detail(tool_id: str):
    """Retrieves full tool metadata, parameter JSON Schema, README documentation, and handler source code."""
    detail = tool_marketplace_service.get_tool_detail(tool_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Marketplace tool '{tool_id}' not found.",
        )
    return detail


@router.post("/scaffold", response_model=ToolScaffoldResponse, status_code=status.HTTP_201_CREATED, summary="Scaffold Tool Boilerplate")
async def scaffold_tool_boilerplate(request: ToolScaffoldRequest):
    """Generates starter code and manifest boilerplate files on disk for creating a new custom tool."""
    try:
        result = tool_marketplace_service.scaffold_new_tool(
            tool_id=request.tool_id,
            name=request.name,
            category=request.category,
            description=request.description,
            author=request.author,
            tags=request.tags,
            parameters=request.parameters,
        )
        return ToolScaffoldResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed scaffolding tool: {str(e)}",
        )


@router.post("/upload", response_model=ToolActionResponse, status_code=status.HTTP_201_CREATED, summary="Upload & Register Custom Tool")
async def upload_custom_tool(request: ToolUploadRequest):
    """Uploads and activates a custom tool bundle (manifest + handler code) dynamically into the server."""
    try:
        result = tool_marketplace_service.upload_custom_tool(
            tool_id=request.tool_id,
            manifest_dict=request.manifest,
            handler_code=request.handler_code,
            readme_content=request.readme_content,
        )
        return ToolActionResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed uploading tool '{request.tool_id}': {str(e)}",
        )


@router.post("/{tool_id}/install", response_model=ToolActionResponse, summary="Install / Enable Marketplace Tool")
async def install_marketplace_tool(tool_id: str):
    """Enables and hot-loads a marketplace tool into the live Agent registry."""
    try:
        tool_marketplace_service.install_tool(tool_id)
        return ToolActionResponse(
            tool_id=tool_id,
            status="installed",
            message=f"Tool '{tool_id}' enabled and registered successfully.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error installing tool '{tool_id}': {str(e)}",
        )


@router.post("/{tool_id}/uninstall", response_model=ToolActionResponse, summary="Uninstall / Disable Marketplace Tool")
async def uninstall_marketplace_tool(tool_id: str):
    """Disables and unregisters a marketplace tool from the live Agent registry."""
    try:
        tool_marketplace_service.uninstall_tool(tool_id)
        return ToolActionResponse(
            tool_id=tool_id,
            status="uninstalled",
            message=f"Tool '{tool_id}' disabled and unregistered from live agents.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error uninstalling tool '{tool_id}': {str(e)}",
        )


@router.delete("/{tool_id}", response_model=ToolActionResponse, summary="Delete Custom Tool")
async def delete_marketplace_tool(tool_id: str):
    """Permanently deletes a custom tool folder from the server."""
    deleted = tool_marketplace_service.delete_custom_tool(tool_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{tool_id}' not found.",
        )
    return ToolActionResponse(
        tool_id=tool_id,
        status="deleted",
        message=f"Tool '{tool_id}' deleted permanently.",
    )
