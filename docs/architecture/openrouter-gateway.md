# Architecture: Centralized OpenRouter Gateway 🌐

## 1. Overview & Rationale

Traditionally, multi-model AI architectures require installing and configuring distinct SDKs for every model provider (`@google/genai`, `openai`, `@anthropic-ai/sdk`, `ollama`). This introduces several severe drawbacks:
1. **API Key Proliferation**: Managing separate billing thresholds, rate limits, and secret keys for 4+ providers.
2. **Inconsistent Tool Calling Interfaces**: Each vendor defines tool parameters and response schemas differently.
3. **Complex Fallbacks**: Writing custom retry logic across incompatible client libraries.

**Muddy Server solves this by centralizing all model access through OpenRouter.**

```
                                  ┌─────────────────────────────┐
                                  │      OpenRouter Gateway     │
                                  │   (https://openrouter.ai)   │
                                  └──────────────┬──────────────┘
                                                 │
          ┌──────────────────────┬───────────────┴──────────────┬──────────────────────┐
          ▼                      ▼                              ▼                      ▼
  Anthropic Claude         OpenAI Models                  Google Gemini          Open-Weights
  - claude-3.7-sonnet      - gpt-4o                       - gemini-2.0-flash     - deepseek-r1
  - claude-3.5-sonnet      - gpt-4o-mini                  - gemini-2.0-pro       - deepseek-v3
  - claude-3-haiku         - o1 / o3-mini                 - gemini-1.5-pro       - llama-3.3-70b
```

---

## 2. Configuration & Alias Resolution

Muddy Server allows developers and downstream clients to use intuitive short names. The configuration in [`app/config/ai.py`](file:///Users/davinci/Documents/sscorp/nischaysharma.com/muddy-server/app/config/ai.py) automatically resolves aliases to official OpenRouter model slugs:

```python
MODEL_ALIASES = {
    # Anthropic
    "claude-3.7-sonnet": "anthropic/claude-3.7-sonnet",
    "claude-3.5-sonnet": "anthropic/claude-3.5-sonnet",
    "claude-3-haiku": "anthropic/claude-3-haiku",
    # OpenAI
    "gpt-4o": "openai/gpt-4o",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "o1": "openai/o1",
    "o3-mini": "openai/o3-mini",
    # Google Gemini
    "gemini-2.0-flash": "google/gemini-2.0-flash-001",
    "gemini-2.0-pro": "google/gemini-2.0-pro-exp-02-05:free",
    # DeepSeek
    "deepseek-r1": "deepseek/deepseek-r1",
    "deepseek-v3": "deepseek/deepseek-chat",
    # Meta Llama
    "llama-3.3-70b": "meta-llama/llama-3.3-70b-instruct",
}
```

If a client requests `model="claude-3.5-sonnet"`, the server automatically formats the request for `anthropic/claude-3.5-sonnet`. If a client passes an explicit full slug (e.g. `mistralai/mistral-large-2407`), it is passed through directly.

---

## 3. LangChain Native Integration

The OpenRouter provider in [`app/providers/ai/openrouter.py`](file:///Users/davinci/Documents/sscorp/nischaysharma.com/muddy-server/app/providers/ai/openrouter.py) instantiates a standard LangChain `ChatOpenAI` client:

```python
from langchain_openai import ChatOpenAI
from app.config import settings

def get_chat_model(model_name: str, temperature: float = 0.7, streaming: bool = True):
    resolved_model = settings.MODEL_ALIASES.get(model_name.lower(), model_name)
    
    headers = {
        "HTTP-Referer": settings.OPENROUTER_SITE_URL,
        "X-Title": settings.OPENROUTER_APP_NAME,
    }
    
    return ChatOpenAI(
        model=resolved_model,
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,  # https://openrouter.ai/api/v1
        temperature=temperature,
        streaming=streaming,
        default_headers=headers,
        timeout=settings.REQUEST_TIMEOUT_SECONDS,
        max_retries=settings.MAX_RETRIES,
    )
```

---

## 4. End-to-End Request Flow

1. **Client Request**: Downstream client calls `POST /api/v1/compute/llm/generate` with `prompt="Draft summary"`, `model="gpt-4o"`.
2. **Controller**: Validates payload via `LLMGenerateRequest` schema and delegates to `llm_service.generate()`.
3. **Service**: Retrieves active provider from `get_llm_provider("openrouter")`.
4. **Provider**: Resolves `gpt-4o` ➔ `openai/gpt-4o`, adds app attribution headers, and invokes OpenRouter via HTTP/2.
5. **Response**: Returns normalized JSON `{ "provider": "openrouter", "model": "openai/gpt-4o", "content": "..." }`.

---

## 5. Offline & Development Mock Mode

If `OPENROUTER_API_KEY` is omitted from `.env`, the provider logs a warning and returns `MockChatModel()`. This allows all agent workflows, tool calling tests, and UI pipelines to function in local development and continuous integration environments without incurring external costs or network latency.
