"""OpenRouter Centralized Multi-Model Provider."""

from typing import Any, AsyncGenerator, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from app.config import settings
from app.core.exceptions import ModelProviderError
from app.core.logging import logger
from app.providers.ai.base import BaseLLMProvider
from app.providers.ai.mock import MockChatModel


class OpenRouterLLMProvider(BaseLLMProvider):
    """Centralized LLM Provider routing all models through OpenRouter."""

    def _resolve_model_name(self, model_name: Optional[str] = None) -> str:
        raw_model = model_name or settings.OPENROUTER_MODEL
        # Resolve short alias if defined
        return settings.MODEL_ALIASES.get(raw_model.lower(), raw_model)

    def get_chat_model(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        streaming: bool = True,
        **kwargs: Any,
    ) -> BaseChatModel:
        api_key = settings.OPENROUTER_API_KEY
        if not api_key:
            logger.warning("[OpenRouter] OPENROUTER_API_KEY not configured. Falling back to MockChatModel.")
            return MockChatModel()

        resolved_model = self._resolve_model_name(model_name)
        headers = {}
        if settings.OPENROUTER_SITE_URL:
            headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
        if settings.OPENROUTER_APP_NAME:
            headers["X-Title"] = settings.OPENROUTER_APP_NAME

        return ChatOpenAI(
            model=resolved_model,
            api_key=api_key,
            base_url=settings.OPENROUTER_BASE_URL,
            temperature=temperature,
            streaming=streaming,
            default_headers=headers if headers else None,
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
            max_retries=settings.MAX_RETRIES,
        )

    async def generate_text(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        model = self.get_chat_model(model_name=model_name, temperature=temperature, streaming=False)
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        response = await model.ainvoke(messages)
        return str(response.content)

    async def stream_text(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        model = self.get_chat_model(model_name=model_name, temperature=temperature, streaming=True)
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        async for chunk in model.astream(messages):
            if chunk.content:
                yield str(chunk.content)

    @property
    def provider_name(self) -> str:
        return "openrouter"
