"""High-Level Agent Orchestration and Session Service."""

import uuid
from typing import Any, AsyncGenerator, Dict, List, Optional
from app.agents.conversational.agent import conversational_agent
from app.agents.supervisor.supervisor import supervisor_agent
from app.agents.workflow_graph.graph import workflow_graph_agent
from app.config import settings
from app.core.event_bus import event_bus
from app.core.logging import logger
from app.schemas.agent import AgentChatRequest, AgentChatResponse, StreamEvent
from app.services.base_service import BaseService


class AgentService(BaseService):
    """Coordinates conversational agents, cyclic workflow graphs, and multi-agent supervisors."""

    def __init__(self):
        super().__init__("AgentService")

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        """Executes agent chat and records session snapshot in SQL."""
        session_id = request.session_id or str(uuid.uuid4())
        request.session_id = session_id

        # Emit Agent Started Telemetry
        await event_bus.emit("agent.event", {
            "session_id": session_id,
            "status": "started",
            "provider": request.provider,
            "model": request.model,
        })

        response = await conversational_agent.chat(request)

        # Record Session in SQL
        await self._save_session_snapshot(
            session_id=session_id,
            agent_type="conversational",
            provider=response.provider,
            model=response.model,
            state={"message_count": len(response.steps) + 1, "last_response": response.response},
            metadata={"execution_time_ms": response.execution_time_ms},
        )

        # Emit Agent Finished Telemetry
        await event_bus.emit("agent.event", {
            "session_id": session_id,
            "status": "completed",
            "execution_time_ms": response.execution_time_ms,
        })

        return response

    async def stream_chat(self, request: AgentChatRequest) -> AsyncGenerator[StreamEvent, None]:
        """Streams tokens and emits real-time events."""
        session_id = request.session_id or str(uuid.uuid4())
        request.session_id = session_id

        async for event in conversational_agent.stream_chat(request):
            yield event

    async def run_workflow(
        self,
        task: str,
        session_id: Optional[str] = None,
        iterations: int = 2,
    ) -> Dict[str, Any]:
        """Runs the cyclic state graph workflow."""
        sid = session_id or str(uuid.uuid4())
        result = await workflow_graph_agent.run(task=task, session_id=sid, iterations=iterations)
        await self._save_session_snapshot(
            session_id=sid,
            agent_type="workflow_graph",
            provider="default",
            model="default",
            state={"iterations": iterations, "steps": result.get("steps", [])},
            metadata={"status": "completed"},
        )
        return result

    async def run_supervisor(
        self,
        task: str,
        session_id: Optional[str] = None,
        subagents: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Runs multi-agent supervisor coordination."""
        sid = session_id or str(uuid.uuid4())
        response = await supervisor_agent.run(task=task, session_id=sid, subagents=subagents)
        result_dict = {
            "session_id": sid,
            "task": task,
            "status": "completed",
            "supervisor_decision": response.response,
            "steps": [s.model_dump() for s in response.steps],
            "execution_time_ms": response.execution_time_ms,
        }
        await self._save_session_snapshot(
            session_id=sid,
            agent_type="supervisor",
            provider="default",
            model="default",
            state={"subagents": subagents or ["researcher", "coder"], "decision": response.response},
            metadata={"status": "completed"},
        )
        return result_dict

    async def _save_session_snapshot(
        self,
        session_id: str,
        agent_type: str,
        provider: str,
        model: str,
        state: Dict[str, Any],
        metadata: Dict[str, Any],
    ):
        if not settings.ENABLE_SQL_DB:
            return
        try:
            from sqlalchemy import select
            from app.db.session import async_session_factory
            from app.db.models.agent_session import AgentSessionModel

            async with async_session_factory() as session:
                async with session.begin():
                    stmt = select(AgentSessionModel).where(AgentSessionModel.session_id == session_id)
                    existing = await session.scalar(stmt)
                    if existing:
                        existing.state_snapshot = state
                        existing.session_metadata = metadata
                    else:
                        new_sess = AgentSessionModel(
                            session_id=session_id,
                            agent_type=agent_type,
                            provider=provider,
                            model=model,
                            state_snapshot=state,
                            session_metadata=metadata,
                        )
                        session.add(new_sess)
        except Exception as e:
            logger.warning(f"[AgentService] Failed to save session snapshot in SQL: {e}")


agent_service = AgentService()
