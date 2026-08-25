"""SQL Database Model for Transactional Pipeline Logs."""

from typing import Any, Dict, Optional
from sqlalchemy import Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PipelineLogModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Tracks execution traces, step durations, and error logs for transactional pipelines."""

    __tablename__ = "pipeline_logs"

    job_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        index=True,
        nullable=True,
    )
    pipeline_name: Mapped[str] = mapped_column(
        String(128),
        index=True,
        nullable=False,
    )
    step_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="SUCCESS",
        nullable=False,
    )
    duration_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    step_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
