"""Conversational Agent with memory and dynamic tool execution."""

import time
import uuid
from typing import AsyncGenerator, Dict, Any, List, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from app.agents.base import LLMProviderFactory
from app.core.logging import logger
from app.memory.checkpoints import checkpointer
from app.schemas.agent import (
    AgentChatRequest,
    AgentChatResponse,
    AgentStep,
    StreamEvent,
)
from app.schemas.message import ToolCall
from app.tools.registry import registry


class ConversationalAgent:
    """Conversational ReAct Agent backed by LangGraph."""

    def __init__(self):
        self.default_system_prompt = (
            "You are Muddy, an advanced, helpful, and autonomous AI assistant. "
            "You have access to tools for mathematics, system status, and web information search. "
            "Think step-by-step and provide clear, concise answers."
        )

    def _get_agent_graph(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        tool_names: Optional[List[str]] = None,
    ):
        """Builds or returns a compiled LangGraph ReAct agent."""
        llm = LLMProviderFactory.get_model(
            provider=provider,
            model_name=model,
            temperature=temperature,
        )

        lc_tools = registry.to_langchain_tools(tool_names)
        sys_prompt = system_prompt or self.default_system_prompt

        # LangGraph prebuilt create_react_agent
        agent_graph = create_react_agent(
            model=llm,
            tools=lc_tools,
            prompt=sys_prompt,
            checkpointer=checkpointer.get_checkpointer(),
        )
        return agent_graph

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        """Executes a single-turn or multi-turn synchronous agent chat."""
        start_time = time.perf_counter()
        session_id = request.session_id or str(uuid.uuid4())

        agent_graph = self._get_agent_graph(
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            system_prompt=request.system_prompt,
            tool_names=request.tools,
        )

        config = {"configurable": {"thread_id": session_id}}
        inputs = {"messages": [HumanMessage(content=request.message)]}

        steps: List[AgentStep] = []
        tool_calls: List[ToolCall] = []
        final_response_text = ""

        step_counter = 1
        try:
            async for chunk in agent_graph.astream(inputs, config, stream_mode="updates"):
                for node_name, node_update in chunk.items():
                    messages = node_update.get("messages", [])
                    for msg in messages:
                        if isinstance(msg, AIMessage):
                            if msg.tool_calls:
                                for tc in msg.tool_calls:
                                    t_call = ToolCall(
                                        id=tc.get("id", str(uuid.uuid4())),
                                        name=tc.get("name", "unknown"),
                                        arguments=tc.get("args", {}),
                                    )
                                    tool_calls.append(t_call)
                                    steps.append(
                                        AgentStep(
                                            step_number=step_counter,
                                            step_type="tool_call",
                                            content=f"Calling tool '{t_call.name}' with args {t_call.arguments}",
                                        )
                                    )
                                    step_counter += 1
                            if msg.content:
                                final_response_text = str(msg.content)
                        elif isinstance(msg, ToolMessage):
                            steps.append(
                                AgentStep(
                                    step_number=step_counter,
                                    step_type="tool_result",
                                    content=f"Tool '{msg.name}' returned: {str(msg.content)[:200]}",
                                )
                            )
                            step_counter += 1

            if not final_response_text:
                # If mock or direct without streaming
                final_response_text = "Task completed successfully."

        except Exception as e:
            logger.error(f"[ConversationalAgent] Chat execution error: {e}")
            final_response_text = f"Agent execution note: {str(e)}"

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return AgentChatResponse(
            session_id=session_id,
            response=final_response_text,
            agent_type="conversational",
            provider=request.provider or "default",
            model=request.model or "default",
            steps=steps,
            tool_calls=tool_calls,
            execution_time_ms=round(elapsed_ms, 2),
        )

    async def stream_chat(self, request: AgentChatRequest) -> AsyncGenerator[StreamEvent, None]:
        """Streams agent reasoning steps and response chunks as Server-Sent Events (SSE)."""
        session_id = request.session_id or str(uuid.uuid4())

        yield StreamEvent(
            event="init",
            data={"session_id": session_id, "agent_type": "conversational"},
            session_id=session_id,
        )

        agent_graph = self._get_agent_graph(
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            system_prompt=request.system_prompt,
            tool_names=request.tools,
        )

        config = {"configurable": {"thread_id": session_id}}
        inputs = {"messages": [HumanMessage(content=request.message)]}

        try:
            async for chunk in agent_graph.astream(inputs, config, stream_mode="updates"):
                for node_name, node_update in chunk.items():
                    messages = node_update.get("messages", [])
                    for msg in messages:
                        if isinstance(msg, AIMessage):
                            if msg.tool_calls:
                                for tc in msg.tool_calls:
                                    yield StreamEvent(
                                        event="tool_call",
                                        data={
                                            "name": tc.get("name"),
                                            "args": tc.get("args"),
                                            "tool_call_id": tc.get("id"),
                                        },
                                        session_id=session_id,
                                    )
                            if msg.content:
                                yield StreamEvent(
                                    event="delta",
                                    data={"content": str(msg.content)},
                                    session_id=session_id,
                                )
                        elif isinstance(msg, ToolMessage):
                            yield StreamEvent(
                                event="tool_result",
                                data={"name": msg.name, "result": str(msg.content)},
                                session_id=session_id,
                            )

            yield StreamEvent(
                event="final",
                data={"status": "completed", "session_id": session_id},
                session_id=session_id,
            )

        except Exception as e:
            logger.error(f"[ConversationalAgent] Stream error: {e}")
            yield StreamEvent(
                event="error",
                data={"error": str(e)},
                session_id=session_id,
            )


conversational_agent = ConversationalAgent()
