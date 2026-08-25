# About Muddy Server 🚀

**Muddy Server** is a high-performance, modular **Computation-as-a-Service (CaaS)** backend framework built with **Python 3.12**, **FastAPI**, **SQLAlchemy 2.0 Async**, **LangGraph**, and **OpenRouter**.

---

## 🎯 Purpose & Philosophy
Muddy Server was designed to act as an isolated, dedicated computation, AI agent orchestration, and machine learning powerhouse for downstream clients (such as `nischaysharma-server`, web applications, and background worker systems).

### Key Architectural Pillars:
1. **Zero RAM / Process Overhead by Default**:
   - Heavy machine learning libraries (`PyTorch`, `Transformers`, `Ray`) are strictly isolated behind feature flags.
   - When flags are disabled (`ENABLE_ML_TRANSFORMERS=false`, `ENABLE_RAY_COMPUTE=false`), zero additional RAM is allocated and zero background daemons are spawned.
2. **Centralized Multi-Model LLM Gateway via OpenRouter**:
   - Standardizes all AI reasoning and tool-calling through a single gateway endpoint.
   - Allows seamless switching between Claude 3.7/3.5, GPT-4o, Gemini 2.0 Flash/Pro, and DeepSeek R1 using standard short slugs.
3. **Strict Transactional Reliability**:
   - Every multi-step compute pipeline features automated pre-validation, timing telemetry, and **reverse-order rollbacks** if any downstream step fails.
4. **Real-Time Live Telemetry**:
   - Clients track 0–100% progress and live token thoughts over WebSocket channels and Server-Sent Events (SSE).
