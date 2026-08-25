"""Modular Feature Flags Configuration."""

from pydantic import Field
from app.config.base import BaseSettings


class FeatureSettings(BaseSettings):
    """Toggles for enabling/disabling subsystems to control RAM and resource consumption."""

    # Lightweight Subsystems (Active by default)
    ENABLE_LLM_GATEWAY: bool = Field(default=True, description="Enable Gemini, OpenAI, Claude routing")
    ENABLE_AGENTS: bool = Field(default=True, description="Enable LangGraph state machine agents")
    ENABLE_DOCS_ENGINE: bool = Field(default=True, description="Enable documentation & content generation")
    ENABLE_WEBSOCKETS: bool = Field(default=True, description="Enable real-time WS streaming hub")
    ENABLE_SQL_DB: bool = Field(default=True, description="Enable SQL session & checkpoint persistence")

    # Heavy Compute Subsystems (Disabled by default to save RAM)
    ENABLE_ML_TRANSFORMERS: bool = Field(
        default=False,
        description="Enable local HuggingFace PyTorch models (SentenceTransformers, CrossEncoder)",
    )
    ENABLE_RAY_COMPUTE: bool = Field(
        default=False,
        description="Enable Ray cluster & distributed actor pool",
    )
    ENABLE_REDIS_QUEUE: bool = Field(
        default=False,
        description="Enable distributed Redis/Arq task queue (uses in-memory fallback if false)",
    )
