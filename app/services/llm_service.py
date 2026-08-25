"""Centralized LLM Gateway Service."""

from typing import Any, AsyncGenerator, Dict, Optional
from app.config import settings
from app.core.exceptions import FeatureDisabledError
from app.core.logging import logger
from app.providers.ai import get_llm_provider
from app.services.base_service import BaseService


class LLMService(BaseService):
    """Centralized service for multi-model LLM generation and streaming."""

    def __init__(self):
        super().__init__("LLMService")

    async def generate(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Generates text from requested model (defaults to OpenRouter)."""
        if not settings.ENABLE_LLM_GATEWAY:
            raise FeatureDisabledError("LLM_GATEWAY")

        llm_provider = get_llm_provider(provider)
        response_text = await llm_provider.generate_text(
            prompt=prompt,
            model_name=model,
            system_prompt=system_prompt,
            temperature=temperature,
        )

        return {
            "provider": llm_provider.provider_name,
            "model": model or getattr(settings, f"{llm_provider.provider_name.upper()}_MODEL", "default"),
            "content": response_text,
        }

    async def stream(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """Streams text chunks from requested model."""
        if not settings.ENABLE_LLM_GATEWAY:
            raise FeatureDisabledError("LLM_GATEWAY")

        llm_provider = get_llm_provider(provider)
        async for chunk in llm_provider.stream_text(
            prompt=prompt,
            model_name=model,
            system_prompt=system_prompt,
            temperature=temperature,
        ):
            yield chunk


llm_service = LLMService()
