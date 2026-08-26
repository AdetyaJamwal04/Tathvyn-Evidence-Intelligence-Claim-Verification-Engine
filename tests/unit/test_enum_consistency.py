"""Tests for Canonical Enum Taxonomies and Verdict Mappings."""

from tathvyn.common.enums import (
    INTERNAL_TO_PUBLIC_VERDICT,
    EvidenceRelationship,
    InternalVerdict,
    Materiality,
    PublicVerdict,
)


def test_internal_verdict_values() -> None:
    """Verify all 5 internal canonical verdicts exist."""
    expected = {
        "SUPPORTED",
        "REFUTED",
        "PARTIALLY_SUPPORTED",
        "INSUFFICIENT_EVIDENCE",
        "UNVERIFIABLE",
    }
    actual = {v.value for v in InternalVerdict}
    assert actual == expected


def test_public_verdict_values() -> None:
    """Verify all 5 public canonical verdicts exist."""
    expected = {"LIKELY TRUE", "LIKELY FALSE", "PARTIALLY TRUE", "UNVERIFIED", "UNVERIFIABLE"}
    actual = {v.value for v in PublicVerdict}
    assert actual == expected


def test_internal_to_public_verdict_mapping() -> None:
    """Verify deterministic mapping from internal to public verdict."""
    assert INTERNAL_TO_PUBLIC_VERDICT[InternalVerdict.SUPPORTED] == PublicVerdict.LIKELY_TRUE
    assert INTERNAL_TO_PUBLIC_VERDICT[InternalVerdict.REFUTED] == PublicVerdict.LIKELY_FALSE
    assert (
        INTERNAL_TO_PUBLIC_VERDICT[InternalVerdict.PARTIALLY_SUPPORTED]
        == PublicVerdict.PARTIALLY_TRUE
    )
    assert (
        INTERNAL_TO_PUBLIC_VERDICT[InternalVerdict.INSUFFICIENT_EVIDENCE]
        == PublicVerdict.UNVERIFIED
    )
    assert INTERNAL_TO_PUBLIC_VERDICT[InternalVerdict.UNVERIFIABLE] == PublicVerdict.UNVERIFIABLE


def test_evidence_relationship_values() -> None:
    """Verify all 7 evidence relationship categories exist."""
    expected = {
        "SUPPORTS",
        "PARTIALLY_SUPPORTS",
        "CONTRADICTS",
        "PARTIALLY_CONTRADICTS",
        "QUALIFIES",
        "CONTEXTUALIZES",
        "NEUTRAL",
    }
    actual = {r.value for r in EvidenceRelationship}
    assert actual == expected


def test_materiality_values() -> None:
    """Verify materiality categories."""
    assert {m.value for m in Materiality} == {"CRITICAL", "MATERIAL", "CONTEXTUAL"}
