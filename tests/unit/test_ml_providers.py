"""Unit tests for ML & Statistical NLP Providers."""

import pytest
from app.core.exceptions import FeatureDisabledError
from app.providers.ml import (
    LocalTransformerEmbeddingsProvider,
    StatisticalNLPProvider,
)
from app.services.nlp_service import nlp_service


def test_statistical_nlp_tokenization():
    provider = StatisticalNLPProvider()
    tokens = provider.tokenize("The quick brown fox jumps over the lazy dog!")
    assert "quick" in tokens
    assert "fox" in tokens
    assert "the" not in tokens  # Stopword removed


def test_statistical_nlp_similarity():
    provider = StatisticalNLPProvider()
    sim_identical = provider.calculate_similarity("FastAPI and Python", "FastAPI and Python")
    assert sim_identical == 1.0

    sim_partial = provider.calculate_similarity("FastAPI and Python", "FastAPI and Node.js")
    assert 0.0 < sim_partial < 1.0

    sim_different = provider.calculate_similarity("FastAPI Python", "Astronomy telescopes galaxy")
    assert sim_different == 0.0


@pytest.mark.asyncio
async def test_statistical_rerank():
    query = "Python web development"
    docs = [
        "Astrophysics and quantum theory",
        "Python FastAPI backend web framework",
        "Gardening and botany care",
    ]
    ranked = await nlp_service.rerank(query, docs, top_k=2)
    assert len(ranked) == 2
    assert ranked[0]["index"] == 1
    assert "FastAPI" in ranked[0]["document"]


@pytest.mark.asyncio
async def test_transformer_disabled_raises_feature_disabled_error():
    provider = LocalTransformerEmbeddingsProvider()
    with pytest.raises(FeatureDisabledError):
        await provider.embed_documents(["Test document"])
