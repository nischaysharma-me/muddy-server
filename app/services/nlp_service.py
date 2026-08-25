"""Machine Learning and Natural Language Processing Service."""

from typing import Any, Dict, List, Optional
from app.providers.ml import (
    get_embeddings_provider,
    get_nlp_provider,
    get_reranker_provider,
)
from app.services.base_service import BaseService


class NLPService(BaseService):
    """Provides dense embeddings, cross-encoder reranking, and statistical NLP utilities."""

    def __init__(self):
        super().__init__("NLPService")

    def tokenize(self, text: str) -> List[str]:
        """Performs lexical tokenization."""
        return get_nlp_provider().tokenize(text)

    def calculate_lexical_similarity(self, text_a: str, text_b: str) -> float:
        """Calculates token frequency cosine similarity."""
        return get_nlp_provider().calculate_similarity(text_a, text_b)

    async def rerank(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Reranks candidate documents by query relevance."""
        reranker = get_reranker_provider()
        ranked = await reranker.rerank(query, documents, top_k=top_k)
        return [
            {"index": item[0], "score": round(item[1], 4), "document": item[2]}
            for item in ranked
        ]

    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Generates dense embeddings (requires ENABLE_ML_TRANSFORMERS=true)."""
        return await get_embeddings_provider().embed_documents(documents)


nlp_service = NLPService()
