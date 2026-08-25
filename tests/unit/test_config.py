"""Unit tests for Centralized Modular Configuration and Feature Flags."""

import pytest
from app.config import settings, Environment, LLMProviderType, JobStatus, ErrorCode


def test_settings_initialization():
    assert settings.APP_NAME == "Muddy Server"
    assert settings.PORT == 8000
    assert settings.ENVIRONMENT in [Environment.DEVELOPMENT, Environment.TESTING, Environment.PRODUCTION]


def test_feature_flags_defaults():
    # Lightweight features enabled by default
    assert settings.ENABLE_LLM_GATEWAY is True
    assert settings.ENABLE_AGENTS is True
    assert settings.ENABLE_WEBSOCKETS is True
    assert settings.ENABLE_SQL_DB is True

    # Heavy compute features disabled by default (Zero RAM overhead)
    assert settings.ENABLE_ML_TRANSFORMERS is False
    assert settings.ENABLE_RAY_COMPUTE is False
    assert settings.ENABLE_REDIS_QUEUE is False


def test_ai_settings():
    assert settings.DEFAULT_LLM_PROVIDER in [LLMProviderType.GEMINI, LLMProviderType.OPENAI, LLMProviderType.ANTHROPIC, LLMProviderType.MOCK]
    assert settings.REQUEST_TIMEOUT_SECONDS > 0
    assert settings.MAX_RETRIES >= 1


def test_database_settings():
    assert "sqlite" in settings.DATABASE_URL or "postgresql" in settings.DATABASE_URL
