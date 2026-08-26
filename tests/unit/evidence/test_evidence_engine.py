"""Tests for End-to-End EvidenceAssessmentEngine."""

from uuid import uuid4

import pytest

from tathvyn.common.enums import EvidenceRelationship
from tathvyn.common.models.claim import AtomicClaim
from tathvyn.common.models.source import Document, Passage
from tathvyn.evidence.engine import EvidenceAssessmentEngine
from tathvyn.models.mock import MockNLIModel, MockRerankerModel


@pytest.mark.asyncio
async def test_evidence_engine_evaluation_flow() -> None:
    """Verify evidence engine reranks, evaluates stance, clusters, and returns EvidenceState."""
    reranker = MockRerankerModel()
    nli = MockNLIModel(default_relationship=EvidenceRelationship.SUPPORTS)
    engine = EvidenceAssessmentEngine(reranker=reranker, nli_model=nli)

    atomic = AtomicClaim(
        claim_id=uuid4(),
        text="Alexander Fleming discovered penicillin in 1928.",
    )

    doc = Document(
        source_id=uuid4(),
        url="https://example.org/fleming",
        canonical_url="https://example.org/fleming",
        content_hash="mock_hash",
    )

    passage = Passage(
        document_id=doc.document_id,
        sequence_order=0,
        text="Alexander Fleming discovered penicillin in 1928 at St. Mary's Hospital.",
        char_start=0,
        char_end=70,
        token_count=10,
        content_hash="phash",
    )

    docs_map = {doc.document_id: doc}

    state, clusters, conflicts = await engine.evaluate_atomic_claim_evidence(
        atomic_claim=atomic,
        passages=[passage],
        documents_by_id=docs_map,
        top_k=3,
    )

    assert state.atomic_claim_id == atomic.atomic_claim_id
    assert len(state.supporting_evidence) == 1
    assert len(state.contradicting_evidence) == 0
    assert state.coverage_score > 0.0
    assert len(clusters) == 1
    assert len(conflicts) == 0
