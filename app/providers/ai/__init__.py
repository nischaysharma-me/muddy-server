"""LLM Providers Package."""

from typing import Optional
from app.config import settings
from app.providers.ai.anthropic import AnthropicLLMProvider
from app.providers.ai.base import BaseLLMProvider
from app.providers.ai.gemini import GeminiLLMProvider
from app.providers.ai.mock import MockChatModel, MockLLMProvider
from app.providers.ai.openai import OpenAILLMProvider
from app.providers.ai.openrouter import OpenRouterLLMProvider

_providers = {
    "openrouter": OpenRouterLLMProvider(),
    "gemini": GeminiLLMProvider(),
    "openai": OpenAILLMProvider(),
    "anthropic": AnthropicLLMProvider(),
    "mock": MockLLMProvider(),
}


def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
    """Factory returning the requested or default LLM provider."""
    name = (provider_name or settings.DEFAULT_LLM_PROVIDER).lower()
    return _providers.get(name, _providers["openrouter"])


__all__ = [
    "BaseLLMProvider",
    "OpenRouterLLMProvider",
    "GeminiLLMProvider",
    "OpenAILLMProvider",
    "AnthropicLLMProvider",
    "MockLLMProvider",
    "MockChatModel",
    "get_llm_provider",
]
