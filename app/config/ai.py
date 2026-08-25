"""AI and LLM Provider Settings."""

from pydantic import Field
from app.config.base import BaseSettings
from app.config.constants import LLMProviderType


class AISettings(BaseSettings):
    """Configuration for LLM providers, model names, and API keys."""

    DEFAULT_LLM_PROVIDER: LLMProviderType = Field(
        default=LLMProviderType.OPENROUTER,
        description="Active default LLM provider (openrouter, gemini, openai, anthropic, local, mock)",
    )

    # OpenRouter (Unified Model Gateway)
    OPENROUTER_API_KEY: str = Field(default="", description="OpenRouter API Key")
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", description="OpenRouter API Endpoint")
    OPENROUTER_MODEL: str = Field(default="google/gemini-2.0-flash-001", description="Default OpenRouter Model")
    OPENROUTER_SITE_URL: str = Field(default="https://nischaysharma.com", description="App site URL for OpenRouter")
    OPENROUTER_APP_NAME: str = Field(default="Muddy Server", description="App name for OpenRouter")

    # Direct Providers
    # Google Gemini
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    GEMINI_MODEL: str = Field(default="gemini-2.0-flash", description="Default Gemini model")

    # OpenAI
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API Key")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", description="Default OpenAI model")

    # Anthropic
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API Key")
    ANTHROPIC_MODEL: str = Field(default="claude-3-5-sonnet-20241022", description="Default Claude model")

    # Local / Ollama
    LOCAL_LLM_BASE_URL: str = Field(default="http://localhost:11434/v1", description="Local LLM endpoint")
    LOCAL_LLM_MODEL: str = Field(default="llama3.2:1b", description="Default Local model name")

    # Timeouts & Retries
    REQUEST_TIMEOUT_SECONDS: float = Field(default=60.0, description="HTTP request timeout in seconds")
    MAX_RETRIES: int = Field(default=3, description="Max retries for transient provider failures")
