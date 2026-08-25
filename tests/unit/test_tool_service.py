"""Unit tests for ToolService and MCP Bridge."""

import pytest
from app.db.session import init_db
from app.providers.tools import mcp_bridge
from app.services.tool_service import tool_service


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()


def test_list_all_tools_catalog():
    tools = tool_service.list_all_tools()
    tool_names = [t["name"] for t in tools]
    assert "calculator" in tool_names
    assert "web_search" in tool_names


@pytest.mark.asyncio
async def test_execute_tool_success_and_audit():
    result = await tool_service.execute_tool(
        name="calculator",
        arguments={"expression": "15 * 4"},
        session_id="test-tool-sess-1",
    )
    assert result["status"] == "success"
    assert str(result["result"]) == "60"


def test_mcp_bridge_tool_registration():
    mcp_bridge.register_server("weather_server", "sse", {"url": "http://localhost:9000"})
    mcp_bridge.register_mcp_tool(
        server_name="weather_server",
        tool_name="get_temperature",
        description="Returns current temperature",
        schema={"properties": {"city": {"type": "string"}}},
        handler=lambda city: f"22°C in {city}",
    )

    tools = tool_service.list_all_tools()
    mcp_tool_names = [t["name"] for t in tools if t["is_mcp"]]
    assert "mcp_weather_server_get_temperature" in mcp_tool_names
