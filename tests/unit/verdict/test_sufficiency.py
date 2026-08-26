"""Tests for Evidence Sufficiency Gate."""

from uuid import uuid4

from tathvyn.common.enums import EvidenceRelationship
from tathvyn.common.models.evidence import Evidence
from tathvyn.verdict.sufficiency import calculate_evidence_sufficiency


def test_empty_evidence_insufficient() -> None:
    """Verify empty evidence returns Q_suff = 0.0."""
    result = calculate_evidence_sufficiency([])
    assert result.is_sufficient is False
    assert result.sufficiency_score == 0.0


def test_sufficient_evidence_calculation() -> None:
    """Verify corroborating evidence exceeds sufficiency threshold."""
    ev1 = Evidence(
        atomic_claim_id=uuid4(),
        passage_id=uuid4(),
        relationship=EvidenceRelationship.SUPPORTS,
        relevance_score=0.95,
        source_quality_score=0.90,
        independence_score=1.0,
    )
    ev2 = Evidence(
        atomic_claim_id=uuid4(),
        passage_id=uuid4(),
        relationship=EvidenceRelationship.SUPPORTS,
        relevance_score=0.90,
        source_quality_score=0.85,
        independence_score=1.0,
    )

    result = calculate_evidence_sufficiency([ev1, ev2])
    assert result.is_sufficient is True
    assert result.sufficiency_score >= 0.60
