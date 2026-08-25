"""SQL Database Model for Compute Jobs."""

from typing import Any, Dict, Optional
from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.config.constants import JobStatus
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class JobModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Stores execution state and results for background compute jobs."""

    __tablename__ = "compute_jobs"

    status: Mapped[str] = mapped_column(
        String(32),
        default=JobStatus.PENDING.value,
        index=True,
        nullable=False,
    )
    progress: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    stage: Mapped[str] = mapped_column(
        String(64),
        default="INITIALIZING",
        nullable=False,
    )
    job_type: Mapped[str] = mapped_column(
        String(64),
        default="generic_compute",
        index=True,
        nullable=False,
    )
    trace_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        index=True,
        nullable=True,
    )
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    execution_time_ms: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
