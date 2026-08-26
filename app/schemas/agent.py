"""Agent Request, Response, and Streaming Event Schemas."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from app.schemas.message import Message, ToolCall, ToolResult


AgentType = Literal["conversational", "workflow", "supervisor"]
ModelProviderType = Literal["openrouter", "gemini", "openai", "anthropic", "local", "mock"]


class AgentChatRequest(BaseModel):
    """Payload for invoking an agent chat or streaming session."""

    message: str = Field(..., description="User prompt or input message")
    session_id: Optional[str] = Field(
        default=None, description="Unique conversation session ID for persistence"
    )
    agent_type: AgentType = Field(
        default="conversational", description="Type of agent to invoke"
    )
    provider: Optional[ModelProviderType] = Field(
        default=None, description="LLM provider override (gemini, openai, anthropic, mock)"
    )
    model: Optional[str] = Field(
        default=None, description="Specific model name override (e.g. gemini-2.0-flash, gpt-4o)"
    )
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Sampling temperature"
    )
    system_prompt: Optional[str] = Field(
        default=None, description="Optional custom system prompt"
    )
    tools: Optional[List[str]] = Field(
        default=None, description="List of tool names allowed for this invocation"
    )


class AgentStep(BaseModel):
    """Represents an intermediate reasoning step taken by the agent."""

    step_number: int
    step_type: Literal["thought", "tool_call", "tool_result", "plan", "reflect"]
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentChatResponse(BaseModel):
    """Synchronous response payload from an agent."""

    session_id: str
    response: str
    agent_type: str
    provider: str
    model: str
    steps: List[AgentStep] = Field(default_factory=list)
    tool_calls: List[ToolCall] = Field(default_factory=list)
    execution_time_ms: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StreamEventType:
    """Event types emitted during agent streaming."""

    EVENT_INIT = "init"
    EVENT_THOUGHT = "thought"
    EVENT_TOOL_CALL = "tool_call"
    EVENT_TOOL_RESULT = "tool_result"
    EVENT_DELTA = "delta"
    EVENT_FINAL = "final"
    EVENT_ERROR = "error"


class StreamEvent(BaseModel):
    """Server-Sent Event payload emitted to the client."""

    event: str = Field(description="Event name, e.g. 'delta', 'thought', 'tool_call', 'final'")
    data: Dict[str, Any] = Field(description="Arbitrary structured event payload")
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkflowState(BaseModel):
    """State model for LangGraph multi-node workflow execution."""

    session_id: str
    goal: str
    current_step: int = 0
    max_steps: int = 10
    plan: List[str] = Field(default_factory=list)
    history: List[Dict[str, Any]] = Field(default_factory=list)
    intermediate_results: Dict[str, Any] = Field(default_factory=dict)
    final_output: Optional[str] = None
    is_completed: bool = False
    error: Optional[str] = None


class WorkflowRequest(BaseModel):
    """Request to initiate a multi-step LangGraph workflow."""

    goal: str = Field(..., description="High-level goal or task for the workflow agent")
    session_id: Optional[str] = Field(default=None, description="Optional session ID")
    max_steps: int = Field(default=8, ge=1, le=20, description="Max reasoning iterations")
    provider: Optional[ModelProviderType] = None
    model: Optional[str] = None


class WorkflowResponse(BaseModel):
    """Response returned from a multi-step LangGraph workflow."""

    session_id: str
    goal: str
    plan: List[str] = Field(default_factory=list)
    observations: List[str] = Field(default_factory=list)
    final_output: str
    steps_executed: int
    is_completed: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

