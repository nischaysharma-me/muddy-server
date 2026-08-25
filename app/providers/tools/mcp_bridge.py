"""Model Context Protocol (MCP) Client Bridge."""

from typing import Any, Dict, List, Optional
from langchain_core.tools import StructuredTool, BaseTool
from app.core.logging import logger


class MCPClientBridge:
    """Manages connections to external Model Context Protocol (MCP) servers and maps their tools."""

    def __init__(self):
        self._connected_servers: Dict[str, Dict[str, Any]] = {}
        self._mcp_tools: Dict[str, Dict[str, Any]] = {}

    def register_server(self, server_name: str, transport: str, config: Dict[str, Any]):
        """Registers an external MCP server endpoint."""
        self._connected_servers[server_name] = {
            "name": server_name,
            "transport": transport,
            "config": config,
            "tools": [],
        }
        logger.info(f"🔌 [MCP] Registered MCP server '{server_name}' ({transport})")

    def register_mcp_tool(
        self,
        server_name: str,
        tool_name: str,
        description: str,
        schema: Dict[str, Any],
        handler: Any,
    ):
        """Registers a tool discovered from an MCP server."""
        full_name = f"mcp_{server_name}_{tool_name}"
        self._mcp_tools[full_name] = {
            "server": server_name,
            "name": tool_name,
            "full_name": full_name,
            "description": description,
            "schema": schema,
            "handler": handler,
        }
        logger.debug(f"[MCP] Registered MCP tool: '{full_name}'")

    def list_mcp_tools(self) -> List[Dict[str, Any]]:
        return list(self._mcp_tools.values())

    def get_langchain_tools(self) -> List[BaseTool]:
        """Converts registered MCP tools into LangChain BaseTool instances."""
        tools = []
        for name, meta in self._mcp_tools.items():
            handler = meta["handler"]
            tool = StructuredTool.from_function(
                coroutine=handler if hasattr(handler, "__call__") else None,
                func=handler if not hasattr(handler, "__call__") else None,
                name=meta["full_name"],
                description=f"[MCP:{meta['server']}] {meta['description']}",
            )
            tools.append(tool)
        return tools


# Global MCP Bridge Singleton
mcp_bridge = MCPClientBridge()
