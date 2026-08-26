"""Tests for Stateful LangGraph Research Graph Runner and AdaptiveResearchEngine."""

import pytest

from tathvyn.common.enums import InternalVerdict, PublicVerdict, ResearchDepth, ResearchStateStatus
from tathvyn.evidence.engine import EvidenceAssessmentEngine
from tathvyn.models.mock import MockNLIModel, MockRerankerModel
from tathvyn.orchestration.engine import AdaptiveResearchEngine
from tathvyn.orchestration.graph import ResearchGraphRunner
from tathvyn.retrieval.providers.mock import MockDocumentFetcher, MockSearchProvider


@pytest.mark.asyncio
async def test_research_graph_fast_mode() -> None:
    """Verify FAST mode completes verification with zero iterative loops."""
    search_mock = MockSearchProvider()
    fetch_mock = MockDocumentFetcher(
        default_template="The speed of light in vacuum is exactly 299,792,458 meters per second by international definition."
    )
    reranker_mock = MockRerankerModel()
    nli_mock = MockNLIModel()
    ev_engine = EvidenceAssessmentEngine(reranker=reranker_mock, nli_model=nli_mock)

    runner = ResearchGraphRunner(
        search_provider=search_mock,
        document_fetcher=fetch_mock,
        evidence_engine=ev_engine,
    )

    decision, state = await runner.execute_research(
        claim_text="The speed of light in vacuum is 299,792,458 meters per second.",
        depth=ResearchDepth.FAST,
    )

    assert decision.verdict == InternalVerdict.SUPPORTED
    assert decision.public_label == PublicVerdict.LIKELY_TRUE
    assert state.status == ResearchStateStatus.COMPLETED
    assert len(state.atomic_claims) >= 1


@pytest.mark.asyncio
async def test_adaptive_research_engine_verify() -> None:
    """Verify AdaptiveResearchEngine high-level interface."""
    search_mock = MockSearchProvider()
    fetch_mock = MockDocumentFetcher(
        default_template="Alexander Fleming discovered penicillin in 1928 at St. Mary's Hospital."
    )
    reranker_mock = MockRerankerModel()
    nli_mock = MockNLIModel()
    ev_engine = EvidenceAssessmentEngine(reranker=reranker_mock, nli_model=nli_mock)

    engine = AdaptiveResearchEngine(
        search_provider=search_mock,
        document_fetcher=fetch_mock,
        evidence_engine=ev_engine,
    )

    decision, state = await engine.verify(
        claim_text="Alexander Fleming discovered penicillin in 1928.",
        depth=ResearchDepth.STANDARD,
    )

    assert decision.verdict == InternalVerdict.SUPPORTED
    assert len(decision.citations) >= 1
    assert state.status == ResearchStateStatus.COMPLETED
