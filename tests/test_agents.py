"""Test Agent API Endpoints and Workflow Execution."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_tools_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/tools")
        assert response.status_code == 200
        tools = response.json()
        assert len(tools) >= 3


@pytest.mark.asyncio
async def test_conversational_agent_chat():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Calculate the square root of 144",
            "provider": "mock",
        }
        response = await client.post("/api/v1/agents/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["agent_type"] == "conversational"
        assert "session_id" in data


@pytest.mark.asyncio
async def test_workflow_graph_run():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "goal": "Audit system diagnostics and formulate report",
            "max_steps": 4,
        }
        response = await client.post("/api/v1/agents/workflow/run", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["is_completed"] is True
        assert len(data["plan"]) > 0
        assert len(data["observations"]) > 0
        assert "final_output" in data


@pytest.mark.asyncio
async def test_supervisor_agent():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Orchestrate multi-step research and system diagnostics",
            "agent_type": "supervisor",
        }
        response = await client.post("/api/v1/agents/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "supervisor"
        assert len(data["steps"]) >= 4


@pytest.mark.asyncio
async def test_stream_agent_chat():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Stream this test response",
            "provider": "mock",
        }
        response = await client.post("/api/v1/agents/stream", json=payload)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")
        content = response.text
        assert "event: init" in content or "event: final" in content or "event: delta" in content

