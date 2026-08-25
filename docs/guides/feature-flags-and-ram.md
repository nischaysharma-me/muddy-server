# Guide: Feature Flags & Zero-RAM Optimization ⚙️

How Muddy Server isolates heavy machine learning and compute clusters to ensure a minimal RAM footprint when only running LLM agents or lightweight APIs.

---

## 🛡️ Feature Flags (`.env`)

```env
# Enable/Disable Subsystems
ENABLE_LLM_GATEWAY=true
ENABLE_AGENTS=true
ENABLE_WEBSOCKETS=true
ENABLE_SQL_DB=true
ENABLE_DOCS_ENGINE=true

# Heavy Compute Subsystems (Disabled by default: Zero RAM waste)
ENABLE_ML_TRANSFORMERS=false
ENABLE_RAY_COMPUTE=false
ENABLE_REDIS_QUEUE=false
```

---

## ⚡ How Lazy Loading Works
- When `ENABLE_ML_TRANSFORMERS=false`, PyTorch and HuggingFace SentenceTransformers are never imported into Python process memory.
- When `ENABLE_RAY_COMPUTE=false`, Ray background daemons, plasma stores, and gRPC servers are never launched.
- If an endpoint requiring a disabled subsystem is called, the server raises `FeatureDisabledError` (`403 Forbidden` / `400 Bad Request`) cleanly without crashing or leaking memory.
