"""Unit tests for Multi-Model LLM Gateway and OpenRouter Provider."""

import pytest
from app.providers.ai import get_llm_provider
from app.providers.ai.openrouter import OpenRouterLLMProvider
from app.services.llm_service import llm_service


@pytest.mark.asyncio
async def test_llm_provider_factory_and_openrouter():
    provider = get_llm_provider("openrouter")
    assert isinstance(provider, OpenRouterLLMProvider)
    assert provider.provider_name == "openrouter"


@pytest.mark.asyncio
async def test_llm_service_generate_and_stream():
    # Uses mock fallback in test environment
    result = await llm_service.generate("Generate article title", provider="mock")
    assert "Mock LLM Response" in result["content"]

    streamed_chunks = []
    async for chunk in llm_service.stream("Stream test", provider="mock"):
        streamed_chunks.append(chunk)

    assert len(streamed_chunks) > 0
    assert "".join(streamed_chunks).startswith("[Mock LLM")
