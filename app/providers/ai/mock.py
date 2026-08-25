"""Mock LLM Provider for testing and fallback."""

import asyncio
from typing import Any, AsyncGenerator, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from app.providers.ai.base import BaseLLMProvider


class MockChatModel(BaseChatModel):
    """Deterministic Mock Chat Model."""

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> Any:
        last_msg = messages[-1].content if messages else "Hello"
        return AIMessage(content=f"[Mock LLM Response]: Processed '{last_msg}'")

    async def _agenerate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> Any:
        last_msg = messages[-1].content if messages else "Hello"
        generation = ChatGeneration(message=AIMessage(content=f"[Mock LLM Response]: Processed '{last_msg}'"))
        return ChatResult(generations=[generation])

    def bind_tools(self, tools: Any, **kwargs: Any) -> "MockChatModel":
        return self

    @property
    def _llm_type(self) -> str:
        return "mock"


class MockLLMProvider(BaseLLMProvider):
    """Deterministic Mock Provider."""

    def get_chat_model(self, model_name: Optional[str] = None, temperature: float = 0.7, streaming: bool = True, **kwargs) -> BaseChatModel:
        return MockChatModel()

    async def generate_text(self, prompt: str, model_name: Optional[str] = None, system_prompt: Optional[str] = None, temperature: float = 0.7, **kwargs) -> str:
        return f"[Mock LLM Response]: Processed '{prompt}'"

    async def stream_text(self, prompt: str, model_name: Optional[str] = None, system_prompt: Optional[str] = None, temperature: float = 0.7, **kwargs) -> AsyncGenerator[str, None]:
        tokens = ["[Mock ", "LLM ", "Streaming ", "Response]: ", prompt]
        for token in tokens:
            await asyncio.sleep(0.01)
            yield token

    @property
    def provider_name(self) -> str:
        return "mock"
