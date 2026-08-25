"""SQL Database Model for Agent Sessions and Memory Checkpoints."""

from typing import Any, Dict, Optional
from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AgentSessionModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Stores conversation threads, checkpoints, and multi-agent memory."""

    __tablename__ = "agent_sessions"

    session_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )
    agent_type: Mapped[str] = mapped_column(
        String(64),
        default="conversational",
        index=True,
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(
        String(64),
        default="openrouter",
        nullable=False,
    )
    model: Mapped[str] = mapped_column(
        String(128),
        default="default",
        nullable=False,
    )
    state_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    session_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
