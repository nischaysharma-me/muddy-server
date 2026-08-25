"""Base Agent Interface and LLM Provider Factory."""

import os
from typing import Any, Dict, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from app.config import settings
from app.core.exceptions import ModelProviderError
from app.core.logging import logger


class MockChatModel(BaseChatModel):
    """Deterministic Mock Chat Model for testing, offline development, and fallback."""

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> Any:
        last_msg = messages[-1].content if messages else "Hello"
        response_text = (
            f"[Muddy-Server Agent Demo Mode]: Processed request: '{last_msg}'. "
            "Configure GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY in .env for live model execution."
        )
        return AIMessage(content=response_text)

    async def _agenerate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> Any:
        from langchain_core.outputs import ChatGeneration, ChatResult
        last_msg = messages[-1].content if messages else "Hello"
        response_text = (
            f"[Muddy-Server Agent Demo Mode]: Processed request: '{last_msg}'. "
            "Configure GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY in .env for live model execution."
        )
        generation = ChatGeneration(message=AIMessage(content=response_text))
        return ChatResult(generations=[generation])

    def bind_tools(self, tools: Any, **kwargs: Any) -> "MockChatModel":
        return self

    @property
    def _llm_type(self) -> str:
        return "mock"


class LLMProviderFactory:
    """Factory to initialize Chat Model instances based on provider and configurations."""

    @staticmethod
    def get_model(
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        streaming: bool = True,
    ) -> BaseChatModel:
        """Returns the appropriate LangChain BaseChatModel instance."""
        active_provider = (provider or settings.DEFAULT_LLM_PROVIDER).lower()

        try:
            if active_provider == "openrouter":
                api_key = settings.OPENROUTER_API_KEY or os.getenv("OPENROUTER_API_KEY")
                if not api_key:
                    logger.warning("[LLMFactory] OPENROUTER_API_KEY not configured. Falling back to MockChatModel.")
                    return MockChatModel()

                raw_model = model_name or settings.OPENROUTER_MODEL
                target_model = settings.MODEL_ALIASES.get(raw_model.lower(), raw_model)

                headers = {}
                if getattr(settings, "OPENROUTER_SITE_URL", None):
                    headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
                if getattr(settings, "OPENROUTER_APP_NAME", None):
                    headers["X-Title"] = settings.OPENROUTER_APP_NAME

                return ChatOpenAI(
                    model=target_model,
                    api_key=api_key,
                    base_url=settings.OPENROUTER_BASE_URL,
                    temperature=temperature,
                    streaming=streaming,
                    default_headers=headers if headers else None,
                )

            elif active_provider == "gemini":
                api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
                if not api_key:
                    logger.warning("[LLMFactory] GEMINI_API_KEY not configured. Falling back to MockChatModel.")
                    return MockChatModel()
                target_model = model_name or settings.GEMINI_MODEL
                return ChatGoogleGenerativeAI(
                    model=target_model,
                    google_api_key=api_key,
                    temperature=temperature,
                    streaming=streaming,
                )

            elif active_provider == "openai":
                api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
                if not api_key:
                    logger.warning("[LLMFactory] OPENAI_API_KEY not configured. Falling back to MockChatModel.")
                    return MockChatModel()
                target_model = model_name or settings.OPENAI_MODEL
                return ChatOpenAI(
                    model=target_model,
                    api_key=api_key,
                    temperature=temperature,
                    streaming=streaming,
                )

            elif active_provider == "anthropic":
                api_key = settings.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    logger.warning("[LLMFactory] ANTHROPIC_API_KEY not configured. Falling back to MockChatModel.")
                    return MockChatModel()
                target_model = model_name or settings.ANTHROPIC_MODEL
                return ChatAnthropic(
                    model=target_model,
                    api_key=api_key,
                    temperature=temperature,
                    streaming=streaming,
                )

            elif active_provider == "mock":
                return MockChatModel()

            else:
                logger.warning(f"[LLMFactory] Unknown provider '{active_provider}'. Using MockChatModel.")
                return MockChatModel()

        except Exception as e:
            logger.error(f"[LLMFactory] Error creating model for provider '{active_provider}': {e}")
            return MockChatModel()
