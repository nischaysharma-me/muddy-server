"""Unit tests for LangGraph Agent Service, Checkpointing, and Supervisors."""

import pytest
from app.db.session import init_db
from app.schemas.agent import AgentChatRequest
from app.services.agent_service import agent_service


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()


@pytest.mark.asyncio
async def test_agent_service_chat_and_snapshot():
    request = AgentChatRequest(
        message="Explain distributed consensus algorithms",
        provider="mock",
    )
    response = await agent_service.chat(request)
    assert response.session_id is not None
    assert "Processed request" in response.response


@pytest.mark.asyncio
async def test_agent_service_run_workflow():
    result = await agent_service.run_workflow(
        task="Draft technical architecture review",
        iterations=2,
    )
    assert result["status"] == "completed"
    assert "final_summary" in result


@pytest.mark.asyncio
async def test_agent_service_run_supervisor():
    result = await agent_service.run_supervisor(
        task="Build an authenticated API with unit tests",
        subagents=["researcher", "coder"],
    )
    assert result["status"] == "completed"
    assert "supervisor_decision" in result
