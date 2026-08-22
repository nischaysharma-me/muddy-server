"""LangGraph State Checkpointer & Session Memory."""

from typing import Dict, Any, Optional
from langgraph.checkpoint.memory import MemorySaver
from app.config import settings
from app.core.logging import logger


class CheckpointManager:
    """Manages checkpointer instances for LangGraph multi-turn session retention."""

    def __init__(self):
        self._memory_saver = MemorySaver()
        self._checkpointer_type = settings.CHECKPOINTER_TYPE
        logger.info(f"[CheckpointManager] Initialized checkpointer with type: {self._checkpointer_type}")

    def get_checkpointer(self):
        """Returns the active checkpointer for LangGraph compilation."""
        # Returns MemorySaver instance; can easily be expanded to AsyncSqliteSaver
        return self._memory_saver


checkpointer = CheckpointManager()
