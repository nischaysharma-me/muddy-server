"""Unit tests for Documentation Indexing Service and API Endpoints."""

from starlette.testclient import TestClient
from app.main import app
from app.services.docs_service import docs_service

client = TestClient(app)


def test_docs_service_tree_indexing():
    tree = docs_service.get_documentation_tree()
    assert len(tree) >= 4
    section_names = [s["section"] for s in tree]
    assert "about" in section_names
    assert "architecture" in section_names
    assert "api" in section_names
    assert "guides" in section_names


def test_docs_service_get_document():
    doc = docs_service.get_document("about", "application")
    assert doc is not None
    assert doc["section"] == "about"
    assert "Muddy Server" in doc["title"]
    assert "Computation-as-a-Service" in doc["content"]


def test_docs_api_endpoints():
    tree_res = client.get("/api/v1/docs/tree")
    assert tree_res.status_code == 200
    assert len(tree_res.json()) >= 4

    doc_res = client.get("/api/v1/docs/about/application")
    assert doc_res.status_code == 200
    assert "content" in doc_res.json()

    raw_res = client.get("/api/v1/docs/about/application/raw")
    assert raw_res.status_code == 200
    assert "Computation-as-a-Service" in raw_res.text


def test_documentation_html_portal():
    portal_res = client.get("/documentation")
    assert portal_res.status_code == 200
    assert "Documentation Portal" in portal_res.text
    assert "marked.min.js" in portal_res.text
