"""SQL Database Model for Tool and MCP Audit Logs."""

from typing import Any, Dict, Optional
from sqlalchemy import Boolean, Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ToolLogModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Audit log tracking every tool execution and external MCP server call."""

    __tablename__ = "tool_audit_logs"

    session_id: Mapped[Optional[str]] = mapped_column(
        String(128),
        index=True,
        nullable=True,
    )
    tool_name: Mapped[str] = mapped_column(
        String(128),
        index=True,
        nullable=False,
    )
    is_mcp: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    arguments: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    is_error: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    duration_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
