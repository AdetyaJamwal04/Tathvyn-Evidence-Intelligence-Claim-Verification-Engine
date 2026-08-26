"""Tests for Synchronous Claim Verification REST Route."""

import pytest
from httpx import ASGITransport, AsyncClient

from tathvyn.api.app import create_app
from tathvyn.evidence.engine import EvidenceAssessmentEngine
from tathvyn.models.mock import MockNLIModel, MockRerankerModel
from tathvyn.orchestration.engine import AdaptiveResearchEngine
from tathvyn.retrieval.providers.mock import MockDocumentFetcher, MockSearchProvider


@pytest.mark.asyncio
async def test_sync_check_claim_fast_mode() -> None:
    """Verify POST /api/v1/check returns valid verification response."""
    app = create_app()

    # Inject deterministic mock engine into app state
    search_mock = MockSearchProvider()
    fetch_mock = MockDocumentFetcher(
        default_template="The speed of light in vacuum is exactly 299,792,458 meters per second."
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
        payload = {
            "claim": "The speed of light in vacuum is 299,792,458 meters per second.",
            "depth": "FAST",
        }
        response = await client.post("/api/v1/check", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["verdict"] == "SUPPORTED"
        assert data["public_label"] == "LIKELY TRUE"
        assert data["confidence"] > 0.5
        assert len(data["citations"]) >= 1
        assert data["latency_ms"] >= 0


@pytest.mark.asyncio
async def test_sync_check_unverifiable_opinion() -> None:
    """Verify POST /api/v1/check handles subjective opinion claims."""
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "claim": "Vanilla ice cream tastes significantly better than chocolate ice cream.",
            "depth": "FAST",
        }
        response = await client.post("/api/v1/check", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["verdict"] == "UNVERIFIABLE"
        assert data["public_label"] == "UNVERIFIABLE"
        assert data["confidence"] == 1.0
