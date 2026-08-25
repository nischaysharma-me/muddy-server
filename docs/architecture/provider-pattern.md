# Architecture: Provider Pattern 🔌

## 1. Concept & Rationale

The **Provider Pattern** is a software design pattern that decouples high-level application orchestration (services and controllers) from low-level infrastructure, cloud vendors, and computation engines.

In Muddy Server:
- **No Direct Vendor Coupling**: Services never import third-party SDKs directly.
- **Uniform Interfaces**: Concrete providers implement Python Abstract Base Classes (`abc.ABC`).
- **Dynamic Swapping**: Changing AI providers (e.g. from OpenRouter to direct OpenAI or Mock) or Queues (Memory vs. Redis) requires modifying only an environment variable.

---

## 2. The Four Provider Tiers

```
                        ┌────────────────────────┐
                        │      Service Layer     │
                        └───────────┬────────────┘
                                    │
    ┌─────────────────┬─────────────┴───────────┬─────────────────┐
    ▼                 ▼                         ▼                 ▼
AI Providers     Compute Engines          Queue Providers     ML Providers
(BaseLLMProvider) (BaseComputeEngine)    (BaseQueue)        (BaseEmbeddingsProvider)
- OpenRouter      - ProcessPool (default) - Memory (default) - Statistical (default)
- Gemini / OpenAI - Ray (lazy cluster)    - Redis Arq        - Cross-Encoder (lazy)
```

---

## 3. Tier Deep Dives

### 1. AI Model Providers (`app/providers/ai/`)
- Interface: `BaseLLMProvider`
  - `get_chat_model(model_name, temperature, streaming) -> BaseChatModel`
  - `generate_text(prompt, system_prompt, model_name) -> str`
  - `stream_text(prompt, system_prompt, model_name) -> AsyncIterator[str]`
- Implementations:
  - `OpenRouterLLMProvider` (Primary unified multi-model gateway).
  - `GeminiLLMProvider` (Direct Google Generative AI integration).
  - `OpenAILLMProvider` (Direct OpenAI API integration).
  - `AnthropicLLMProvider` (Direct Anthropic API integration).
  - `MockLLMProvider` (Offline deterministic mock for zero-cost testing).

### 2. Compute Engines (`app/providers/compute/`)
- Interface: `BaseComputeEngine`
  - `execute(func, *args, **kwargs) -> Any`
  - `map(func, iterable) -> List[Any]`
- Implementations:
  - `ProcessPoolComputeEngine`: Default standard Python multiprocessing executor. Zero background daemons, zero extra RAM.
  - `RayComputeEngine`: Lazy-loaded distributed actor pool for massive parallel cluster compute.

### 3. Asynchronous Task Queues (`app/providers/queues/`)
- Interface: `BaseQueue`
  - `enqueue(job_id, task_func, *args, **kwargs) -> str`
  - `get_status(job_id) -> Optional[str]`
  - `cancel(job_id) -> bool`
- Implementations:
  - `MemoryQueue`: Default asyncio background task worker returning instant `< 5ms` job submissions.
  - `RedisArqQueue`: Distributed Redis worker queue for multi-replica deployments.

### 4. Natural Language & ML Providers (`app/providers/ml/`)
- Interfaces: `BaseEmbeddingsProvider`, `BaseRerankerProvider`, `BaseNLPProvider`
- Implementations:
  - `StatisticalNLPProvider`: Zero-torch TF-IDF / BM25 lexical tokenization and candidate reranker.
  - `LocalTransformerEmbeddingsProvider`: Lazy HuggingFace SentenceTransformer encoder.
  - `CrossEncoderRerankerProvider`: Lazy neural cross-encoder.
