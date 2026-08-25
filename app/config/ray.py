"""Ray Distributed Compute Configuration."""

from typing import Optional
from pydantic import Field
from app.config.base import BaseSettings


class RaySettings(BaseSettings):
    """Configuration for Ray distributed actor cluster."""

    RAY_ADDRESS: Optional[str] = Field(
        default=None,
        description="Ray cluster address (e.g. 'auto' or 'ray://<host>:10001'). None for local embedded cluster.",
    )
    RAY_NUM_CPUS: Optional[int] = Field(default=None, description="Max CPU cores allocated to Ray")
    RAY_NUM_GPUS: Optional[int] = Field(default=None, description="Max GPUs allocated to Ray")
    RAY_INCLUDE_DASHBOARD: bool = Field(default=False, description="Start Ray web dashboard")
    RAY_LOG_TO_DRIVER: bool = Field(default=True, description="Forward actor logs to driver")
