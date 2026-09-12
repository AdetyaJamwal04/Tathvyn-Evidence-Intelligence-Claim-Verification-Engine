"""Tests for Conservative Atomic Decomposition and Anti-Hallucination Gate."""

from uuid import uuid4

from tathvyn.claims.decomposer import decompose_claim
from tathvyn.common.enums import ClaimType, Materiality
from tathvyn.common.models.claim import Claim


def test_already_atomic_claim_preservation() -> None:
    """Verify single proposition is preserved with is_atomic=True and depth=1."""
    text = "The James Webb Space Telescope operates around the Sun-Earth Lagrange Point 2."
    claim = Claim(
        request_id=uuid4(),
        raw_text=text,
        normalized_text=text,
        primary_type=ClaimType.FACTUAL,
        content_hash="mock_hash_1",
    )
    atomic_claims = decompose_claim(claim)
    assert len(atomic_claims) == 1
    assert atomic_claims[0].is_atomic is True
    assert atomic_claims[0].materiality == Materiality.CRITICAL
    assert atomic_claims[0].decomposition_depth <= 1


def test_compound_claim_decomposition() -> None:
    """Verify multi-clause compound assertions are segmented into atomic claims."""
    text = "Google was founded by Larry Page and Sergey Brin in September 1998, and its initial IPO raised $50 billion on the NYSE in 2000."
    claim = Claim(
        request_id=uuid4(),
        raw_text=text,
        normalized_text=text,
        primary_type=ClaimType.COMPOUND,
        content_hash="mock_hash_2",
    )
    atomic_claims = decompose_claim(claim)
    assert len(atomic_claims) == 2
    assert atomic_claims[0].materiality == Materiality.CRITICAL
    assert atomic_claims[1].materiality == Materiality.MATERIAL
    assert all(ac.decomposition_depth <= 1 for ac in atomic_claims)
