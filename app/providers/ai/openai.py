"""Direct OpenAI LLM Provider."""

from typing import Any, AsyncGenerator, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from app.config import settings
from app.core.logging import logger
from app.providers.ai.base import BaseLLMProvider
from app.providers.ai.mock import MockChatModel


class OpenAILLMProvider(BaseLLMProvider):
    """Direct OpenAI Provider."""

    def get_chat_model(self, model_name: Optional[str] = None, temperature: float = 0.7, streaming: bool = True, **kwargs) -> BaseChatModel:
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            logger.warning("[OpenAI] OPENAI_API_KEY not configured. Falling back to MockChatModel.")
            return MockChatModel()

        return ChatOpenAI(
            model=model_name or settings.OPENAI_MODEL,
            api_key=api_key,
            temperature=temperature,
            streaming=streaming,
        )

    async def generate_text(self, prompt: str, model_name: Optional[str] = None, system_prompt: Optional[str] = None, temperature: float = 0.7, **kwargs) -> str:
        model = self.get_chat_model(model_name=model_name, temperature=temperature, streaming=False)
        res = await model.ainvoke([HumanMessage(content=prompt)])
        return str(res.content)

    async def stream_text(self, prompt: str, model_name: Optional[str] = None, system_prompt: Optional[str] = None, temperature: float = 0.7, **kwargs) -> AsyncGenerator[str, None]:
        model = self.get_chat_model(model_name=model_name, temperature=temperature, streaming=True)
        async for chunk in model.astream([HumanMessage(content=prompt)]):
            if chunk.content:
                yield str(chunk.content)

    @property
    def provider_name(self) -> str:
        return "openai"
