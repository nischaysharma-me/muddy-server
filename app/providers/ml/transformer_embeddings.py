"""Local Transformer Embeddings Provider (Lazy-Loaded)."""

import asyncio
from typing import List, Optional
from app.config import settings
from app.core.exceptions import FeatureDisabledError
from app.core.logging import logger
from app.providers.ml.base import BaseEmbeddingsProvider


class LocalTransformerEmbeddingsProvider(BaseEmbeddingsProvider):
    """Dense vector embedding provider using local Hugging Face / Sentence-Transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _ensure_model_loaded(self):
        if not settings.ENABLE_ML_TRANSFORMERS:
            raise FeatureDisabledError("ML_TRANSFORMERS")

        if self._model is not None:
            return self._model

        try:
            logger.info(f"🧠 [ML] Loading local embedding model '{self.model_name}'...")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"✅ [ML] Embedding model '{self.model_name}' loaded successfully.")
            return self._model
        except ImportError as err:
            logger.error(f"[ML] sentence_transformers is not installed: {err}")
            raise FeatureDisabledError("ML_TRANSFORMERS (sentence-transformers not installed)") from err
        except Exception as e:
            logger.error(f"[ML] Failed to load embedding model: {e}")
            raise e

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        model = self._ensure_model_loaded()
        loop = asyncio.get_running_loop()
        embeddings = await loop.run_in_executor(None, model.encode, texts)
        return embeddings.tolist()

    async def embed_query(self, text: str) -> List[float]:
        docs = await self.embed_documents([text])
        return docs[0]
