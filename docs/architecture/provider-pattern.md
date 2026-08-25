# Architecture: Provider Pattern 🔌

The **Provider Pattern** in Muddy Server abstracts underlying technologies, external APIs, and compute clusters behind uniform, contract-bound interfaces.

---

## 1. AI Providers (`app/providers/ai/`)
- Abstract base class: `BaseLLMProvider` (`get_chat_model()`, `generate_text()`, `stream_text()`).
- Implementations:
  - `OpenRouterLLMProvider` (Primary unified multi-model provider).
  - `GeminiLLMProvider` (Direct Google Generative AI).
  - `OpenAILLMProvider` (Direct OpenAI).
  - `AnthropicLLMProvider` (Direct Anthropic).
  - `MockLLMProvider` (Deterministic fallback for offline & CI/CD).

---

## 2. Compute Providers (`app/providers/compute/`)
- Abstract base class: `BaseComputeEngine` (`execute()`, `map()`).
- Implementations:
  - `ProcessPoolComputeEngine` (Zero-RAM, zero-daemon standard multiprocessing).
  - `RayComputeEngine` (Lazy-loaded distributed Ray actor cluster).

---

## 3. Queue Providers (`app/providers/queues/`)
- Abstract base class: `BaseQueue` (`enqueue()`, `get_status()`, `cancel()`).
- Implementations:
  - `MemoryQueue` (Zero-dependency async task queue).
  - `RedisArqQueue` (Distributed Redis queue for high-throughput production).

---

## 4. Machine Learning Providers (`app/providers/ml/`)
- Abstract interfaces: `BaseEmbeddingsProvider`, `BaseRerankerProvider`, `BaseNLPProvider`.
- Implementations:
  - `StatisticalNLPProvider` (Zero-torch TF-IDF / BM25 lexical scorer).
  - `LocalTransformerEmbeddingsProvider` (Lazy HuggingFace transformer encoder).
  - `CrossEncoderRerankerProvider` (Lazy neural cross-encoder).
