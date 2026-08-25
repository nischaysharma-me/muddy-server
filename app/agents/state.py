"""LangGraph Agent State Definitions."""

import operator
from typing import Annotated, Any, Dict, List, Optional, Sequence
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """Shared state for multi-agent workflows and cyclic state graphs."""

    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str
    session_id: str
    plan: Optional[List[str]]
    current_step: int
    scratchpad: Dict[str, Any]
    next_worker: Optional[str]
    is_finished: bool
