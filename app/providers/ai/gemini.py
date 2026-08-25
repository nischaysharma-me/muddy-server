"""Direct Google Gemini LLM Provider."""

from typing import Any, AsyncGenerator, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings
from app.core.logging import logger
from app.providers.ai.base import BaseLLMProvider
from app.providers.ai.mock import MockChatModel


class GeminiLLMProvider(BaseLLMProvider):
    """Direct Google Gemini Provider."""

    def get_chat_model(self, model_name: Optional[str] = None, temperature: float = 0.7, streaming: bool = True, **kwargs) -> BaseChatModel:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.warning("[Gemini] GEMINI_API_KEY not configured. Falling back to MockChatModel.")
            return MockChatModel()

        return ChatGoogleGenerativeAI(
            model=model_name or settings.GEMINI_MODEL,
            google_api_key=api_key,
            temperature=temperature,
            streaming=streaming,
        )

    async def generate_text(self, prompt: str, model_name: Optional[str] = None, system_prompt: Optional[str] = None, temperature: float = 0.7, **kwargs) -> str:
        model = self.get_chat_model(model_name=model_name, temperature=temperature, streaming=False)
        messages = [HumanMessage(content=prompt)]
        res = await model.ainvoke(messages)
        return str(res.content)

    async def stream_text(self, prompt: str, model_name: Optional[str] = None, system_prompt: Optional[str] = None, temperature: float = 0.7, **kwargs) -> AsyncGenerator[str, None]:
        model = self.get_chat_model(model_name=model_name, temperature=temperature, streaming=True)
        async for chunk in model.astream([HumanMessage(content=prompt)]):
            if chunk.content:
                yield str(chunk.content)

    @property
    def provider_name(self) -> str:
        return "gemini"
