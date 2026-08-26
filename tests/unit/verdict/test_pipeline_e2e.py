"""End-to-End Tests for VeriFact MVP Verification Pipeline."""

import pytest

from tathvyn.common.enums import InternalVerdict, PublicVerdict
from tathvyn.evidence.engine import EvidenceAssessmentEngine
from tathvyn.models.mock import MockNLIModel, MockRerankerModel
from tathvyn.retrieval.providers.mock import MockDocumentFetcher, MockSearchProvider
from tathvyn.verdict.pipeline import VeriFactPipeline


@pytest.mark.asyncio
async def test_pipeline_e2e_supported_claim() -> None:
    """Verify end-to-end flow from raw claim to SUPPORTED VerdictDecision."""
    search_mock = MockSearchProvider()
    fetch_mock = MockDocumentFetcher()
    reranker_mock = MockRerankerModel()
    nli_mock = MockNLIModel()
    ev_engine = EvidenceAssessmentEngine(reranker=reranker_mock, nli_model=nli_mock)

    pipeline = VeriFactPipeline(
        search_provider=search_mock,
        document_fetcher=fetch_mock,
        evidence_engine=ev_engine,
    )

    decision = await pipeline.verify_claim(
        "Is it true that the James Webb Space Telescope operates at Sun-Earth L2?"
    )

    assert decision.verdict == InternalVerdict.SUPPORTED
    assert decision.public_label == PublicVerdict.LIKELY_TRUE
    assert decision.confidence > 0.60
    assert len(decision.citations) >= 1
    assert "James Webb" in decision.summary_text


@pytest.mark.asyncio
async def test_pipeline_e2e_unverifiable_opinion() -> None:
    """Verify opinion fast-path produces UNVERIFIABLE without network calls."""
    pipeline = VeriFactPipeline()
    decision = await pipeline.verify_claim(
        "Vanilla ice cream tastes significantly better than chocolate ice cream."
    )

    assert decision.verdict == InternalVerdict.UNVERIFIABLE
    assert decision.public_label == PublicVerdict.UNVERIFIABLE
    assert decision.confidence == 1.0
    assert decision.stop_reason == "UNVERIFIABLE"
