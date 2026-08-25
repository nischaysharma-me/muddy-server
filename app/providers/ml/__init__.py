"""Machine Learning & NLP Providers Package."""

from app.config import settings
from app.providers.ml.base import (
    BaseEmbeddingsProvider,
    BaseNLPProvider,
    BaseRerankerProvider,
)
from app.providers.ml.reranker import CrossEncoderRerankerProvider
from app.providers.ml.statistical_nlp import StatisticalNLPProvider
from app.providers.ml.transformer_embeddings import LocalTransformerEmbeddingsProvider

_default_nlp_provider: StatisticalNLPProvider = None
_default_transformer_embeddings: LocalTransformerEmbeddingsProvider = None
_default_cross_encoder: CrossEncoderRerankerProvider = None


def get_nlp_provider() -> BaseNLPProvider:
    """Returns the zero-overhead statistical NLP provider."""
    global _default_nlp_provider
    if _default_nlp_provider is None:
        _default_nlp_provider = StatisticalNLPProvider()
    return _default_nlp_provider


def get_embeddings_provider() -> BaseEmbeddingsProvider:
    """Returns the transformer embeddings provider."""
    global _default_transformer_embeddings
    if _default_transformer_embeddings is None:
        _default_transformer_embeddings = LocalTransformerEmbeddingsProvider()
    return _default_transformer_embeddings


def get_reranker_provider() -> BaseRerankerProvider:
    """Returns the neural reranker if ML is enabled, otherwise statistical reranker."""
    global _default_cross_encoder
    if settings.ENABLE_ML_TRANSFORMERS:
        if _default_cross_encoder is None:
            _default_cross_encoder = CrossEncoderRerankerProvider()
        return _default_cross_encoder
    return get_nlp_provider()


__all__ = [
    "BaseEmbeddingsProvider",
    "BaseRerankerProvider",
    "BaseNLPProvider",
    "StatisticalNLPProvider",
    "LocalTransformerEmbeddingsProvider",
    "CrossEncoderRerankerProvider",
    "get_nlp_provider",
    "get_embeddings_provider",
    "get_reranker_provider",
]
