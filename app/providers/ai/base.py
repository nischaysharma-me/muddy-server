"""Abstract Base LLM Provider Interface."""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel


class BaseLLMProvider(ABC):
    """Abstract interface for all LLM providers."""

    @abstractmethod
    def get_chat_model(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        streaming: bool = True,
        **kwargs: Any,
    ) -> BaseChatModel:
        """Returns the configured LangChain BaseChatModel instance."""
        raise NotImplementedError

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generates text completion asynchronously."""
        raise NotImplementedError

    @abstractmethod
    async def stream_text(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Streams generated tokens asynchronously."""
        raise NotImplementedError

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns provider identifier."""
        raise NotImplementedError
