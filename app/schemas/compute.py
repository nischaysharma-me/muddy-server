"""Pydantic Schemas for Generic Compute API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class JobSubmissionRequest(BaseModel):
    """Payload to submit a compute job."""

    job_type: str = Field(..., description="Job identifier, e.g. 'article_generation', 'math_simulation'")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Job input parameters")
    run_async: bool = Field(default=True, description="Whether to enqueue in background queue")


class JobSubmissionResponse(BaseModel):
    """Response returned upon submitting a compute job."""

    job_id: str
    status: str
    ws_stream_url: str
    message: str


class NLPRerankRequest(BaseModel):
    """Payload for text candidate reranking."""

    query: str
    documents: List[str]
    top_k: int = 5


class NLPRerankResponse(BaseModel):
    """Response from text candidate reranker."""

    query: str
    results: List[Dict[str, Any]]


class NLPSimilarityRequest(BaseModel):
    """Payload for text similarity."""

    text_a: str
    text_b: str


class NLPSimilarityResponse(BaseModel):
    """Response for text similarity."""

    similarity_score: float


class LLMGenerateRequest(BaseModel):
    """Payload for direct LLM generation."""

    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: float = 0.7


class LLMGenerateResponse(BaseModel):
    """Response from LLM generation."""

    provider: str
    model: str
    content: str
