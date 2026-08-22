"""Tool Discovery and Registry Endpoints."""

from typing import List, Dict, Any
from fastapi import APIRouter
from app.tools.registry import registry, ToolDefinition
from app.tools.mcp.client import mcp_manager

router = APIRouter(prefix="/tools", tags=["Agent Tools"])


@router.get("", response_model=List[ToolDefinition], summary="List Registered Agent Tools")
async def list_tools():
    """Lists all registered Python tools with their auto-extracted parameter schemas."""
    return registry.list_tools()


@router.get("/mcp/servers", summary="List Connected MCP Tool Servers")
async def list_mcp_servers() -> List[Dict[str, Any]]:
    """Returns connected Model Context Protocol (MCP) tool servers."""
    return mcp_manager.list_connected_servers()
