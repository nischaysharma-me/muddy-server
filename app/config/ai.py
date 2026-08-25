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

    # Common Model Aliases mapped to OpenRouter Slugs
    MODEL_ALIASES: dict = {
        # Anthropic Claude
        "claude-3.7-sonnet": "anthropic/claude-3.7-sonnet",
        "claude-3.7-sonnet:thinking": "anthropic/claude-3.7-sonnet:thinking",
        "claude-3.5-sonnet": "anthropic/claude-3.5-sonnet",
        "claude-3.5-haiku": "anthropic/claude-3.5-haiku",
        "claude-3-opus": "anthropic/claude-3-opus",
        "claude-3-haiku": "anthropic/claude-3-haiku",
        
        # OpenAI Models
        "gpt-4o": "openai/gpt-4o",
        "gpt-4o-mini": "openai/gpt-4o-mini",
        "gpt-4.5-preview": "openai/gpt-4.5-preview",
        "o1": "openai/o1",
        "o1-mini": "openai/o1-mini",
        "o1-preview": "openai/o1-preview",
        "o3-mini": "openai/o3-mini",
        "o3-mini-high": "openai/o3-mini-high",
        "chatgpt-4o-latest": "openai/chatgpt-4o-latest",
        
        # Google Gemini Models (Latest 3.x & 2.x Series)
        "gemini-3.7-flash": "google/gemini-3.7-flash",
        "gemini-3.6-flash": "google/gemini-3.6-flash",
        "gemini-3.5-flash-lite": "google/gemini-3.5-flash-lite",
        "gemini-3.1-pro": "google/gemini-3.1-pro",
        "gemini-flash-latest": "google/gemini-flash-latest",
        "gemini-2.0-flash": "google/gemini-2.0-flash-001",
        "gemini-2.0-flash-lite": "google/gemini-2.0-flash-lite-preview-02-05:free",
        "gemini-2.0-pro": "google/gemini-2.0-pro-exp-02-05:free",
        "gemini-2.0-flash-thinking": "google/gemini-2.0-flash-thinking-exp:free",
        "gemini-1.5-pro": "google/gemini-pro-1.5",
        "gemini-1.5-flash": "google/gemini-flash-1.5",
        "gemini-2.0-flash:free": "google/gemini-2.0-flash-001:free",
        
        # DeepSeek
        "deepseek-r1": "deepseek/deepseek-r1",
        "deepseek-r1:free": "deepseek/deepseek-r1:free",
        "deepseek-v3": "deepseek/deepseek-chat",
        "deepseek-v3:free": "deepseek/deepseek-chat:free",
        "deepseek-r1-distill-llama-70b": "deepseek/deepseek-r1-distill-llama-70b",
        "deepseek-r1-distill-qwen-32b": "deepseek/deepseek-r1-distill-qwen-32b",
        
        # Meta Llama
        "llama-3.3-70b": "meta-llama/llama-3.3-70b-instruct",
        "llama-3.3-70b:free": "meta-llama/llama-3.3-70b-instruct:free",
        "llama-3.1-405b": "meta-llama/llama-3.1-405b-instruct",
        "llama-3.1-70b": "meta-llama/llama-3.1-70b-instruct",
        "llama-3.1-8b": "meta-llama/llama-3.1-8b-instruct",
        "llama-3.2-3b": "meta-llama/llama-3.2-3b-instruct",
        "llama-3.2-1b": "meta-llama/llama-3.2-1b-instruct",
        
        # Qwen (Alibaba)
        "qwen-2.5-72b": "qwen/qwen-2.5-72b-instruct",
        "qwen-2.5-coder-32b": "qwen/qwen-2.5-coder-32b-instruct",
        "qwq-32b-preview": "qwen/qwq-32b-preview",
        "qwen-max": "qwen/qwen-max",
        
        # Mistral AI
        "mistral-large": "mistralai/mistral-large-2411",
        "mistral-small": "mistralai/mistral-small-24b-instruct-2501",
        "codestral": "mistralai/codestral-2501",
        "pixtral-large": "mistralai/pixtral-large-2411",
        "ministral-8b": "mistralai/ministral-8b",
        
        # xAI Grok
        "grok-2": "x-ai/grok-2-1212",
        "grok-2-vision": "x-ai/grok-2-vision-1212",
        "grok-beta": "x-ai/grok-beta",
    }
