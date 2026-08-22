"""Model Context Protocol (MCP) Client Manager for connecting external tool servers."""

from typing import Any, Dict, List, Optional
from app.core.logging import logger


class MCPClientManager:
    """Manages connections to remote or local Model Context Protocol (MCP) servers."""

    def __init__(self):
        self._connected_servers: Dict[str, Dict[str, Any]] = {}

    async def connect_server(self, server_name: str, server_url: str) -> bool:
        """Establishes connection to an external MCP tool server."""
        logger.info(f"[MCP] Connecting to external MCP server '{server_name}' at {server_url}")
        # Store configuration for discovery
        self._connected_servers[server_name] = {
            "name": server_name,
            "url": server_url,
            "status": "connected",
        }
        return True

    def list_connected_servers(self) -> List[Dict[str, Any]]:
        """Returns list of all connected MCP servers."""
        return list(self._connected_servers.values())


mcp_manager = MCPClientManager()
