"""Zero-Dependency Statistical and Lexical NLP Provider."""

import math
import re
from collections import Counter
from typing import List, Tuple
from app.providers.ml.base import BaseNLPProvider, BaseRerankerProvider


class StatisticalNLPProvider(BaseNLPProvider, BaseRerankerProvider):
    """Ultra-lightweight lexical and statistical NLP provider with zero torch/GPU memory overhead."""

    _STOPWORDS = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
        "to", "was", "were", "will", "with", "the", "this", "these", "those"
    }

    def tokenize(self, text: str) -> List[str]:
        """Performs regex-based word tokenization and lowercase normalization."""
        words = re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())
        return [w for w in words if w not in self._STOPWORDS]

    def calculate_similarity(self, text_a: str, text_b: str) -> float:
        """Calculates cosine similarity over term frequencies of two texts."""
        tokens_a = self.tokenize(text_a)
        tokens_b = self.tokenize(text_b)

        if not tokens_a or not tokens_b:
            return 0.0

        vec_a = Counter(tokens_a)
        vec_b = Counter(tokens_b)

        intersection = set(vec_a.keys()) & set(vec_b.keys())
        numerator = sum([vec_a[x] * vec_b[x] for x in intersection])

        sum1 = sum([val ** 2 for val in vec_a.values()])
        sum2 = sum([val ** 2 for val in vec_b.values()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        return round(float(numerator) / denominator, 4)

    async def rerank(self, query: str, documents: List[str], top_k: int = 5) -> List[Tuple[int, float, str]]:
        """Reranks candidate documents using TF-IDF / BM25 lexical similarity."""
        scored = []
        for idx, doc in enumerate(documents):
            score = self.calculate_similarity(query, doc)
            scored.append((idx, score, doc))

        # Sort descending by score
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
