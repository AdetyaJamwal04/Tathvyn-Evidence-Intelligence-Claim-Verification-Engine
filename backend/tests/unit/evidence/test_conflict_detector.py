"""Tests for Evidence Conflict Detector."""

from uuid import uuid4

from tathvyn.common.enums import ConflictSeverity, ConflictType, EvidenceRelationship
from tathvyn.common.models.evidence import Evidence
from tathvyn.evidence.conflict_detector import ConflictDetector


def test_direct_contradiction_detection() -> None:
    """Verify opposing support and contradiction evidence generates Conflict."""
    detector = ConflictDetector()
    atomic_id = uuid4()

    ev_support = Evidence(
        atomic_claim_id=atomic_id,
        passage_id=uuid4(),
        relationship=EvidenceRelationship.SUPPORTS,
        entailment_score=0.92,
    )
    ev_contra = Evidence(
        atomic_claim_id=atomic_id,
        passage_id=uuid4(),
        relationship=EvidenceRelationship.CONTRADICTS,
        contradiction_score=0.88,
    )

    conflicts = detector.detect_conflicts(atomic_id, [ev_support, ev_contra])

    assert len(conflicts) == 1
    assert conflicts[0].conflict_type == ConflictType.DIRECT_CONTRADICTION
    assert conflicts[0].severity == ConflictSeverity.CRITICAL


def test_no_conflicts_on_unanimous_support() -> None:
    """Verify unanimous supporting evidence produces no conflicts."""
    detector = ConflictDetector()
    atomic_id = uuid4()

    ev1 = Evidence(
        atomic_claim_id=atomic_id, passage_id=uuid4(), relationship=EvidenceRelationship.SUPPORTS
    )
    ev2 = Evidence(
        atomic_claim_id=atomic_id, passage_id=uuid4(), relationship=EvidenceRelationship.SUPPORTS
    )

    conflicts = detector.detect_conflicts(atomic_id, [ev1, ev2])
    assert len(conflicts) == 0
