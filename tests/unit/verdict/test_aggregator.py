"""Tests for Materiality-Weighted Parent Verdict Aggregator."""

from uuid import uuid4

from tathvyn.common.enums import (
    AtomicClaimVerdict,
    ClaimVerifiability,
    InternalVerdict,
    Materiality,
    PublicVerdict,
)
from tathvyn.common.models.claim import AtomicClaim
from tathvyn.verdict.aggregator import ParentVerdictAggregator


def test_unverifiable_claim_aggregation() -> None:
    """Verify subjective opinion aggregates to UNVERIFIABLE."""
    aggregator = ParentVerdictAggregator()
    res = aggregator.aggregate_verdicts([], claim_verifiability=ClaimVerifiability.UNVERIFIABLE)
    assert res.internal_verdict == InternalVerdict.UNVERIFIABLE
    assert res.public_label == PublicVerdict.UNVERIFIABLE


def test_unanimous_supported_compound_claim() -> None:
    """Verify all atomic propositions supported aggregates to SUPPORTED."""
    aggregator = ParentVerdictAggregator()
    ac1 = AtomicClaim(claim_id=uuid4(), text="Claim part 1", materiality=Materiality.CRITICAL)
    ac2 = AtomicClaim(claim_id=uuid4(), text="Claim part 2", materiality=Materiality.MATERIAL)

    evals = [(ac1, AtomicClaimVerdict.SUPPORTED), (ac2, AtomicClaimVerdict.SUPPORTED)]
    res = aggregator.aggregate_verdicts(evals)

    assert res.internal_verdict == InternalVerdict.SUPPORTED
    assert res.public_label == PublicVerdict.LIKELY_TRUE


def test_mixed_compound_claim_partially_supported() -> None:
    """Verify supported + refuted parts aggregate to PARTIALLY_SUPPORTED."""
    aggregator = ParentVerdictAggregator()
    ac1 = AtomicClaim(claim_id=uuid4(), text="Claim part 1", materiality=Materiality.CRITICAL)
    ac2 = AtomicClaim(claim_id=uuid4(), text="Claim part 2", materiality=Materiality.MATERIAL)

    evals = [(ac1, AtomicClaimVerdict.SUPPORTED), (ac2, AtomicClaimVerdict.REFUTED)]
    res = aggregator.aggregate_verdicts(evals)

    assert res.internal_verdict == InternalVerdict.PARTIALLY_SUPPORTED
    assert res.public_label == PublicVerdict.PARTIALLY_TRUE
    assert res.framing_concerns is True
