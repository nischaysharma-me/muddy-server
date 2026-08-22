"""Test Tool Registry and Custom Domain Tools."""

import pytest
from app.tools.registry import registry
from app.tools.custom.calculator import calculate
from app.tools.custom.system_info import get_system_status
from app.tools.custom.search import web_search_mock


@pytest.mark.asyncio
async def test_tool_registration():
    tools = registry.list_tools()
    tool_names = [t.name for t in tools]
    assert "calculator" in tool_names
    assert "get_system_status" in tool_names
    assert "web_search" in tool_names


@pytest.mark.asyncio
async def test_calculator_tool():
    result = calculate("25 * 4 + 10")
    assert result == "110"

    sqrt_res = calculate("math.sqrt(64)")
    assert float(sqrt_res) == 8.0


@pytest.mark.asyncio
async def test_system_status_tool():
    status = get_system_status()
    assert status["status"] == "online"
    assert "python_version" in status


@pytest.mark.asyncio
async def test_web_search_tool():
    res = await web_search_mock(query="LangGraph agent architecture")
    assert res["query"] == "LangGraph agent architecture"
    assert len(res["results"]) > 0


@pytest.mark.asyncio
async def test_langchain_conversion():
    lc_tools = registry.to_langchain_tools()
    assert len(lc_tools) >= 3
    assert all(hasattr(t, "name") for t in lc_tools)
