"""Cross-Encoder Neural Reranker Provider (Lazy-Loaded)."""

import asyncio
from typing import List, Tuple
from app.config import settings
from app.core.exceptions import FeatureDisabledError
from app.core.logging import logger
from app.providers.ml.base import BaseRerankerProvider


class CrossEncoderRerankerProvider(BaseRerankerProvider):
    """Neural cross-encoder reranker for high-precision semantic ranking."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None

    def _ensure_model_loaded(self):
        if not settings.ENABLE_ML_TRANSFORMERS:
            raise FeatureDisabledError("ML_TRANSFORMERS")

        if self._model is not None:
            return self._model

        try:
            logger.info(f"🧠 [ML] Loading cross-encoder model '{self.model_name}'...")
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name)
            logger.info(f"✅ [ML] Cross-encoder '{self.model_name}' loaded successfully.")
            return self._model
        except ImportError as err:
            raise FeatureDisabledError("ML_TRANSFORMERS (sentence-transformers not installed)") from err
        except Exception as e:
            logger.error(f"[ML] Failed to load cross-encoder: {e}")
            raise e

    async def rerank(self, query: str, documents: List[str], top_k: int = 5) -> List[Tuple[int, float, str]]:
        model = self._ensure_model_loaded()
        pairs = [[query, doc] for doc in documents]
        loop = asyncio.get_running_loop()
        scores = await loop.run_in_executor(None, model.predict, pairs)

        scored = [(idx, float(score), documents[idx]) for idx, score in enumerate(scores)]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
