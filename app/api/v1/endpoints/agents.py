"""Agent Execution, Streaming, and Workflow Endpoints."""

import json
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from sse_starlette.sse import EventSourceResponse
from app.agents.conversational.agent import conversational_agent
from app.agents.workflow_graph.graph import workflow_engine
from app.agents.supervisor.supervisor import supervisor_agent
from app.core.exceptions import AgentHTTPException
from app.core.logging import logger
from app.schemas.agent import (
    AgentChatRequest,
    AgentChatResponse,
    WorkflowRequest,
)

router = APIRouter(prefix="/agents", tags=["Agent Execution"])


@router.post("/chat", response_model=AgentChatResponse, summary="Synchronous Agent Chat")
async def chat_with_agent(request: AgentChatRequest):
    """Executes a turn with the conversational agent and returns full response with step traces."""
    try:
        if request.agent_type == "supervisor":
            return await supervisor_agent.run(request.message, request.session_id)
        else:
            return await conversational_agent.chat(request)
    except Exception as e:
        logger.error(f"[API] Error in agent chat: {e}")
        raise AgentHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}",
        )


@router.post("/stream", summary="Stream Agent Reasoning and Token Output (SSE)")
async def stream_agent_chat(request: AgentChatRequest):
    """Streams agent reasoning steps, tool calls, and text tokens via Server-Sent Events (SSE)."""

    async def event_generator():
        try:
            async for event in conversational_agent.stream_chat(request):
                yield {
                    "event": event.event,
                    "data": json.dumps(event.data),
                }
        except Exception as e:
            logger.error(f"[API] Stream event generator error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }

    return EventSourceResponse(event_generator())


@router.post("/workflow/run", summary="Execute LangGraph Multi-Node State Graph")
async def run_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """Executes a cyclic multi-step LangGraph workflow (Planner -> Executor -> Reflector -> Synthesizer)."""
    try:
        return await workflow_engine.run(request)
    except Exception as e:
        logger.error(f"[API] Error running workflow graph: {e}")
        raise AgentHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow graph execution failed: {str(e)}",
        )


@router.post("/supervisor/run", response_model=AgentChatResponse, summary="Execute Supervisor Multi-Agent Team")
async def run_supervisor(request: AgentChatRequest):
    """Delegates tasks across specialized subagents using the Supervisor pattern."""
    try:
        return await supervisor_agent.run(request.message, request.session_id)
    except Exception as e:
        logger.error(f"[API] Error running supervisor agent: {e}")
        raise AgentHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Supervisor execution failed: {str(e)}",
        )
