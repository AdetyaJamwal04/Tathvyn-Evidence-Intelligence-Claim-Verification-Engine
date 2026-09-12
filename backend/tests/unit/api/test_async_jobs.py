"""Tests for Asynchronous Deep Research Dispatch and Polling."""

import pytest
from httpx import ASGITransport, AsyncClient

from tathvyn.api.app import create_app
from tathvyn.evidence.engine import EvidenceAssessmentEngine
from tathvyn.models.mock import MockNLIModel, MockRerankerModel
from tathvyn.orchestration.engine import AdaptiveResearchEngine
from tathvyn.retrieval.providers.mock import MockDocumentFetcher, MockSearchProvider


@pytest.mark.asyncio
async def test_async_job_dispatch_and_polling() -> None:
    """Verify POST /api/v1/research enqueues job and GET /api/v1/research/{id} polls status."""
    app = create_app()

    search_mock = MockSearchProvider()
    fetch_mock = MockDocumentFetcher(
        default_template="Alexander Fleming discovered penicillin in 1928 at St. Mary's Hospital."
    )
    ev_engine = EvidenceAssessmentEngine(
        reranker=MockRerankerModel(),
        nli_model=MockNLIModel(),
    )
    app.state.research_engine = AdaptiveResearchEngine(
        search_provider=search_mock,
        document_fetcher=fetch_mock,
        evidence_engine=ev_engine,
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Enqueue Job
        payload = {
            "claim": "Alexander Fleming discovered penicillin in 1928.",
            "depth": "DEEP",
        }
        dispatch_resp = await client.post("/api/v1/research", json=payload)
        assert dispatch_resp.status_code == 202
        dispatch_data = dispatch_resp.json()
        job_id = dispatch_data["job_id"]
        assert dispatch_data["status"] == "QUEUED"
        assert f"/api/v1/research/{job_id}" in dispatch_data["polling_url"]

        # 2. Poll Job Status
        poll_resp = await client.get(f"/api/v1/research/{job_id}")
        assert poll_resp.status_code == 200
        poll_data = poll_resp.json()
        assert poll_data["job_id"] == job_id
        assert poll_data["status"] in ("QUEUED", "PROCESSING", "COMPLETED")


@pytest.mark.asyncio
async def test_nonexistent_job_returns_404() -> None:
    """Verify polling unknown job ID returns HTTP 404."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/research/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
