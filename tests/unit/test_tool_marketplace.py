"""Unit tests for Tool Marketplace & Plugin System."""

import json
from pathlib import Path
import pytest
from app.services.tool_marketplace_service import ToolMarketplaceService
from app.tools.plugins.base import PluginManifest
from app.tools.plugins.generator import generate_tool_boilerplate
from app.tools.registry import registry


def test_plugin_manifest_validation():
    manifest_data = {
        "id": "test_analyzer",
        "name": "Test Analyzer",
        "version": "1.0.0",
        "author": "Tester",
        "category": "nlp",
        "tags": ["nlp", "test"],
        "description": "Analyzes test inputs.",
        "enabled": True,
        "parameters": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    }
    manifest = PluginManifest(**manifest_data)
    assert manifest.id == "test_analyzer"
    assert manifest.enabled is True
    assert "text" in manifest.parameters["properties"]


def test_generate_tool_boilerplate():
    files = generate_tool_boilerplate(
        tool_id="sentiment_scorer",
        name="Sentiment Scorer",
        category="nlp",
        description="Scores text sentiment",
        author="Nischay",
    )
    assert "manifest.json" in files
    assert "handler.py" in files
    assert "test_tool.py" in files
    assert "README.md" in files

    manifest_dict = json.loads(files["manifest.json"])
    assert manifest_dict["id"] == "sentiment_scorer"
    assert "SentimentScorerTool" in files["handler.py"]


@pytest.mark.asyncio
async def test_builtin_plugins_discovery_and_execution():
    service = ToolMarketplaceService()
    count = service.discover_and_register_all()
    assert count >= 2

    # Check currency converter execution in registry
    assert "currency_converter" in registry._tools
    conv_result = await registry.execute("currency_converter", amount=100.0, from_currency="USD", to_currency="EUR")
    assert conv_result["converted_amount"] == 92.0

    # Check JSON formatter execution in registry
    assert "json_formatter" in registry._tools
    fmt_result = await registry.execute("json_formatter", raw_json='{"hello":"world"}', indent=2)
    assert fmt_result["valid"] is True
    assert '"hello": "world"' in fmt_result["formatted_json"]


def test_marketplace_filtering_and_search():
    service = ToolMarketplaceService()
    finance_tools = service.list_marketplace_tools(category="finance")
    assert any(t["id"] == "currency_converter" for t in finance_tools)

    searched_tools = service.list_marketplace_tools(search="json")
    assert any(t["id"] == "json_formatter" for t in searched_tools)


@pytest.mark.asyncio
async def test_custom_tool_upload_and_toggle(tmp_path: Path):
    service = ToolMarketplaceService(plugins_dir=tmp_path)

    manifest_dict = {
        "id": "mock_multiplier",
        "name": "Mock Multiplier",
        "version": "1.0.0",
        "author": "Tester",
        "category": "math",
        "tags": ["math"],
        "description": "Multiplies two numbers",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["a", "b"],
        },
    }

    handler_code = """
from app.tools.plugins.base import BaseToolPlugin

class MockMultiplierTool(BaseToolPlugin):
    async def execute(self, a: float, b: float):
        return {"result": a * b}
"""

    # Upload tool
    upload_res = service.upload_custom_tool(
        tool_id="mock_multiplier",
        manifest_dict=manifest_dict,
        handler_code=handler_code,
    )
    assert upload_res["status"] == "installed"

    # Verify execution in registry
    mult_res = await registry.execute("mock_multiplier", a=6, b=7)
    assert mult_res["result"] == 42

    # Uninstall (Disable)
    service.uninstall_tool("mock_multiplier")
    assert "mock_multiplier" not in registry._tools

    # Re-install (Enable)
    service.install_tool("mock_multiplier")
    assert "mock_multiplier" in registry._tools

    # Delete
    deleted = service.delete_custom_tool("mock_multiplier")
    assert deleted is True
    assert "mock_multiplier" not in registry._tools
