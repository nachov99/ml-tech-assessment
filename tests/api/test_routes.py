import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import router, get_service
from app.domain.models import TranscriptAnalysis


@pytest.fixture
def client():
    service = MagicMock()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_service] = lambda: service
    yield TestClient(app), service


def test_analyze_returns_200(client):
    test_client, service = client
    service.analyze.return_value = TranscriptAnalysis(
        id="abc-123", summary="A summary", action_items=["do this"]
    )

    response = test_client.post(
        "/transcripts/analyze", json={"transcript": "hello world"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "abc-123"
    assert data["summary"] == "A summary"
    assert data["action_items"] == ["do this"]


def test_analyze_returns_400_on_empty_transcript(client):
    test_client, service = client
    service.analyze.side_effect = ValueError("Transcript cannot be empty")

    response = test_client.post("/transcripts/analyze", json={"transcript": ""})

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_get_by_id_returns_200(client):
    test_client, service = client
    service.get_by_id.return_value = TranscriptAnalysis(
        id="abc-123", summary="A summary", action_items=["do this"]
    )

    response = test_client.get("/transcripts/abc-123")

    assert response.status_code == 200
    assert response.json()["id"] == "abc-123"


def test_get_by_id_returns_404(client):
    test_client, service = client
    service.get_by_id.return_value = None

    response = test_client.get("/transcripts/nonexistent")

    assert response.status_code == 404


def test_analyze_batch_returns_200(client):
    test_client, service = client
    service.analyze_batch = AsyncMock(
        return_value=[
            TranscriptAnalysis(id="1", summary="s1", action_items=["a1"]),
            TranscriptAnalysis(id="2", summary="s2", action_items=["a2"]),
        ]
    )

    response = test_client.post(
        "/transcripts/analyze-batch",
        json={"transcripts": ["t1", "t2"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 2
    assert data["results"][0]["id"] == "1"
    assert data["results"][1]["id"] == "2"


def test_analyze_batch_returns_400_on_empty_list(client):
    test_client, service = client

    response = test_client.post(
        "/transcripts/analyze-batch", json={"transcripts": []}
    )

    assert response.status_code == 400


def test_analyze_batch_returns_400_on_empty_transcript(client):
    test_client, service = client
    service.analyze_batch = AsyncMock(
        side_effect=ValueError("Transcript cannot be empty")
    )

    response = test_client.post(
        "/transcripts/analyze-batch",
        json={"transcripts": ["valid", ""]},
    )

    assert response.status_code == 400