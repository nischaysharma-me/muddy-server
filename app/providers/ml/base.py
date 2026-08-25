"""Abstract Base Machine Learning and NLP Provider Interfaces."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class BaseEmbeddingsProvider(ABC):
    """Abstract interface for text embedding models."""

    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates dense vector embeddings for a list of documents."""
        raise NotImplementedError

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """Generates a dense vector embedding for a search query."""
        raise NotImplementedError


class BaseRerankerProvider(ABC):
    """Abstract interface for cross-encoder rerankers."""

    @abstractmethod
    async def rerank(self, query: str, documents: List[str], top_k: int = 5) -> List[Tuple[int, float, str]]:
        """Reranks candidate documents given a query, returning (original_index, score, doc)."""
        raise NotImplementedError


class BaseNLPProvider(ABC):
    """Abstract interface for statistical and lexical NLP processing."""

    @abstractmethod
    def tokenize(self, text: str) -> List[str]:
        """Tokenizes text into words/stems."""
        raise NotImplementedError

    @abstractmethod
    def calculate_similarity(self, text_a: str, text_b: str) -> float:
        """Calculates lexical or semantic similarity score between two texts."""
        raise NotImplementedError
