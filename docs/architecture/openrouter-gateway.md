# Architecture: Centralized OpenRouter Gateway 🌐

Muddy Server uses **OpenRouter** as its centralized universal LLM provider. This enables access to leading frontier and open-weights models through a single standardized endpoint (`https://openrouter.ai/api/v1`) using a single API key (`OPENROUTER_API_KEY`).

---

## 🎯 Supported Model Families & Short Aliases

Muddy Server automatically maps user-friendly short names to their OpenRouter slug:

| Short Alias | Target OpenRouter Model Slug | Provider Family |
| :--- | :--- | :--- |
| `claude-3.7-sonnet` | `anthropic/claude-3.7-sonnet` | Anthropic |
| `claude-3.5-sonnet` | `anthropic/claude-3.5-sonnet` | Anthropic |
| `claude-3-haiku` | `anthropic/claude-3-haiku` | Anthropic |
| `gpt-4o` | `openai/gpt-4o` | OpenAI |
| `gpt-4o-mini` | `openai/gpt-4o-mini` | OpenAI |
| `o1` / `o3-mini` | `openai/o1` / `openai/o3-mini` | OpenAI |
| `gemini-2.0-flash` | `google/gemini-2.0-flash-001` | Google |
| `gemini-2.0-pro` | `google/gemini-2.0-pro-exp-02-05:free` | Google |
| `deepseek-r1` | `deepseek/deepseek-r1` | DeepSeek |
| `deepseek-v3` | `deepseek/deepseek-chat` | DeepSeek |
| `llama-3.3-70b` | `meta-llama/llama-3.3-70b-instruct` | Meta |

---

## ⚡ Integration Details
- **LangChain Adapter**: Built on LangChain's `ChatOpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)`.
- **Attribution Headers**: Automatically sends `HTTP-Referer` and `X-Title` for OpenRouter model leaderboard rankings.
- **Fallback**: If `OPENROUTER_API_KEY` is not provided in `.env`, the server automatically defaults to `MockChatModel` for offline development and testing.
