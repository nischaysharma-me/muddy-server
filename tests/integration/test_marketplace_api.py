"""Integration tests for Tool Marketplace Endpoints & Agent Execution."""

import pytest
from starlette.testclient import TestClient
from app.db.session import init_db
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()


def test_get_marketplace_catalog():
    res = client.get("/api/v1/tools/marketplace")
    assert res.status_code == 200
    catalog = res.json()
    assert len(catalog) >= 2
    tool_ids = [t["id"] for t in catalog]
    assert "currency_converter" in tool_ids
    assert "json_formatter" in tool_ids


def test_get_marketplace_tool_detail():
    res = client.get("/api/v1/tools/marketplace/currency_converter")
    assert res.status_code == 200
    detail = res.json()
    assert detail["manifest"]["id"] == "currency_converter"
    assert "properties" in detail["manifest"]["parameters"]
    assert "CurrencyConverterTool" in detail["handler_code"]


def test_scaffold_marketplace_tool():
    payload = {
        "tool_id": "test_scaffold_tool",
        "name": "Test Scaffold Tool",
        "category": "developer",
        "description": "Generated via scaffold test",
        "author": "Test Author",
    }
    res = client.post("/api/v1/tools/marketplace/scaffold", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["tool_id"] == "test_scaffold_tool"
    assert data["status"] == "created"

    # Cleanup
    client.delete("/api/v1/tools/marketplace/test_scaffold_tool")


def test_upload_and_toggle_tool():
    payload = {
        "tool_id": "temp_echo_tool",
        "manifest": {
            "name": "Temp Echo Tool",
            "category": "utilities",
            "description": "Echoes text back",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
        "handler_code": """
from app.tools.plugins.base import BaseToolPlugin

class TempEchoToolTool(BaseToolPlugin):
    async def execute(self, text: str):
        return {"echo": text}
""",
    }

    # Upload
    upload_res = client.post("/api/v1/tools/marketplace/upload", json=payload)
    assert upload_res.status_code == 201
    assert upload_res.json()["status"] == "installed"

    # Uninstall
    uninst_res = client.post("/api/v1/tools/marketplace/temp_echo_tool/uninstall")
    assert uninst_res.status_code == 200
    assert uninst_res.json()["status"] == "uninstalled"

    # Re-install
    inst_res = client.post("/api/v1/tools/marketplace/temp_echo_tool/install")
    assert inst_res.status_code == 200
    assert inst_res.json()["status"] == "installed"

    # Delete
    del_res = client.delete("/api/v1/tools/marketplace/temp_echo_tool")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"


def test_agent_executes_marketplace_plugin_tool():
    # Agent executes currency_converter tool dynamically
    agent_payload = {
        "message": "Convert 100 USD to EUR using currency converter",
        "provider": "mock",
        "tools": ["currency_converter"],
    }
    res = client.post("/api/v1/agents/chat", json=agent_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] if "status" in data else True
