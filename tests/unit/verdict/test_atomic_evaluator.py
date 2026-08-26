"""Tests for Atomic Claim Verdict Evaluator."""

from uuid import uuid4

from tathvyn.common.enums import AtomicClaimVerdict, EvidenceRelationship
from tathvyn.common.models.evidence import Evidence, EvidenceState
from tathvyn.verdict.atomic_evaluator import AtomicClaimVerdictEvaluator


def test_atomic_evaluation_supported() -> None:
    """Verify strong supporting evidence leads to SUPPORTED atomic verdict."""
    evaluator = AtomicClaimVerdictEvaluator()
    atomic_id = uuid4()

    ev = Evidence(
        atomic_claim_id=atomic_id,
        passage_id=uuid4(),
        relationship=EvidenceRelationship.SUPPORTS,
        entailment_score=0.92,
        relevance_score=0.95,
        independence_score=1.0,
    )

    state = EvidenceState(
        atomic_claim_id=atomic_id,
        supporting_evidence=[ev],
        contradicting_evidence=[],
        context_evidence=[],
    )

    result = evaluator.evaluate_atomic_claim(state)
    assert result.verdict == AtomicClaimVerdict.SUPPORTED
    assert result.confidence > 0.60


def test_atomic_evaluation_refuted() -> None:
    """Verify strong refuting evidence leads to REFUTED atomic verdict."""
    evaluator = AtomicClaimVerdictEvaluator()
    atomic_id = uuid4()

    ev = Evidence(
        atomic_claim_id=atomic_id,
        passage_id=uuid4(),
        relationship=EvidenceRelationship.CONTRADICTS,
        contradiction_score=0.94,
        relevance_score=0.95,
        independence_score=1.0,
    )

    state = EvidenceState(
        atomic_claim_id=atomic_id,
        supporting_evidence=[],
        contradicting_evidence=[ev],
        context_evidence=[],
    )

    result = evaluator.evaluate_atomic_claim(state)
    assert result.verdict == AtomicClaimVerdict.REFUTED
    assert result.confidence > 0.60


def test_atomic_evaluation_conflicted() -> None:
    """Verify unresolved conflict leads to CONFLICTED atomic verdict."""
    evaluator = AtomicClaimVerdictEvaluator()
    atomic_id = uuid4()

    state = EvidenceState(
        atomic_claim_id=atomic_id,
        supporting_evidence=[],
        contradicting_evidence=[],
        unresolved_conflict=True,
    )

    result = evaluator.evaluate_atomic_claim(state)
    assert result.verdict == AtomicClaimVerdict.CONFLICTED
