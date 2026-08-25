"""Generic Compute Endpoints for Submitting Jobs, Reranking, and LLM Operations."""

import asyncio
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from sse_starlette.sse import EventSourceResponse
from app.core.exceptions import MuddyServerException
from app.core.logging import logger
from app.schemas.compute import (
    JobSubmissionRequest,
    JobSubmissionResponse,
    LLMGenerateRequest,
    LLMGenerateResponse,
    NLPRerankRequest,
    NLPRerankResponse,
    NLPSimilarityRequest,
    NLPSimilarityResponse,
)
from app.services.job_service import job_service
from app.services.llm_service import llm_service
from app.services.nlp_service import nlp_service

router = APIRouter(prefix="/compute", tags=["Compute Services & Jobs"])


async def _generic_job_executor(job_id: str, payload: Dict[str, Any]):
    """Default worker function executing a generic background compute job."""
    from app.core.event_bus import event_bus
    await asyncio.sleep(0.05)
    await event_bus.emit("job.progress", {
        "job_id": job_id,
        "stage": "PROCESSING_PAYLOAD",
        "progress_pct": 50.0,
    })
    await asyncio.sleep(0.05)


@router.post("/jobs", response_model=JobSubmissionResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_compute_job(request: JobSubmissionRequest):
    """Submits a compute job to the asynchronous job queue."""
    try:
        job_id = await job_service.create_and_enqueue(
            job_type=request.job_type,
            payload=request.payload,
            task_func=_generic_job_executor,
        )

        return JobSubmissionResponse(
            job_id=job_id,
            status="queued",
            ws_stream_url=f"/api/v1/ws/jobs/{job_id}",
            message="Compute job accepted and queued successfully.",
        )
    except Exception as e:
        logger.error(f"[API] Error submitting job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}", response_model=Dict[str, Any])
async def get_job_status(job_id: str):
    """Retrieves current job status, progress (0-100%), stage, and result."""
    job_info = await job_service.get_job(job_id)
    if not job_info:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return job_info


@router.delete("/jobs/{job_id}")
async def cancel_compute_job(job_id: str):
    """Cancels a queued or executing compute job."""
    cancelled = await job_service.cancel_job(job_id)
    return {"job_id": job_id, "cancelled": cancelled}


@router.post("/nlp/rerank", response_model=NLPRerankResponse)
async def rerank_documents(request: NLPRerankRequest):
    """Reranks candidate documents based on query relevance score."""
    ranked = await nlp_service.rerank(
        query=request.query,
        documents=request.documents,
        top_k=request.top_k,
    )
    return NLPRerankResponse(query=request.query, results=ranked)


@router.post("/nlp/similarity", response_model=NLPSimilarityResponse)
async def calculate_similarity(request: NLPSimilarityRequest):
    """Calculates lexical/statistical similarity between two texts."""
    score = nlp_service.calculate_lexical_similarity(request.text_a, request.text_b)
    return NLPSimilarityResponse(similarity_score=score)


@router.post("/llm/generate", response_model=LLMGenerateResponse)
async def generate_llm(request: LLMGenerateRequest):
    """Direct multi-model LLM generation (via OpenRouter or specified provider)."""
    result = await llm_service.generate(
        prompt=request.prompt,
        provider=request.provider,
        model=request.model,
        system_prompt=request.system_prompt,
        temperature=request.temperature,
    )
    return LLMGenerateResponse(
        provider=result["provider"],
        model=result["model"],
        content=result["content"],
    )


@router.post("/llm/stream")
async def stream_llm(request: LLMGenerateRequest):
    """Streams LLM tokens as Server-Sent Events (SSE)."""
    async def event_generator():
        async for chunk in llm_service.stream(
            prompt=request.prompt,
            provider=request.provider,
            model=request.model,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
        ):
            yield {"event": "delta", "data": chunk}
        yield {"event": "done", "data": "[DONE]"}

    return EventSourceResponse(event_generator())
