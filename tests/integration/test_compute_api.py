"""Integration tests for Generic Compute REST Endpoints."""

import pytest
from starlette.testclient import TestClient
from app.db.session import init_db
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()


def test_submit_and_get_compute_job():
    payload = {
        "job_type": "article_simulation",
        "payload": {"prompt": "AI Architectures in 2026"},
    }
    response = client.post("/api/v1/compute/jobs", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    assert "/ws/jobs/" in data["ws_stream_url"]

    # Get status
    job_id = data["job_id"]
    status_res = client.get(f"/api/v1/compute/jobs/{job_id}")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["job_id"] == job_id


def test_cancel_compute_job():
    payload = {
        "job_type": "cancellable_job",
        "payload": {},
    }
    submit_res = client.post("/api/v1/compute/jobs", json=payload)
    job_id = submit_res.json()["job_id"]

    delete_res = client.delete(f"/api/v1/compute/jobs/{job_id}")
    assert delete_res.status_code == 200
    assert delete_res.json()["cancelled"] is True


def test_nlp_rerank_endpoint():
    payload = {
        "query": "FastAPI async backend",
        "documents": [
            "Quantum physics and relativity",
            "FastAPI high performance async web APIs in Python",
            "Cooking recipes for Italian pasta",
        ],
        "top_k": 2,
    }
    response = client.post("/api/v1/compute/nlp/rerank", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 2
    assert data["results"][0]["index"] == 1


def test_nlp_similarity_endpoint():
    payload = {
        "text_a": "Machine Learning and Neural Networks",
        "text_b": "Machine Learning and Deep Neural Networks",
    }
    response = client.post("/api/v1/compute/nlp/similarity", json=payload)
    assert response.status_code == 200
    assert response.json()["similarity_score"] > 0.5


def test_llm_generate_endpoint():
    payload = {
        "prompt": "Hello world from test suite",
        "provider": "mock",
    }
    response = client.post("/api/v1/compute/llm/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Mock LLM Response" in data["content"]
