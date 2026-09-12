"""Tests for Temporal Overlap and Alignment Validator."""

from tathvyn.evidence.validators.temporal_validator import validate_temporal_alignment


def test_matching_temporal_year() -> None:
    """Verify exact year match."""
    claim = "Apollo 11 landed on the Moon in 1969."
    evidence = "In July 1969, Neil Armstrong stepped onto the lunar surface."
    result = validate_temporal_alignment(claim, evidence)

    assert result.is_temporally_valid is True
    assert result.status == "VALID"


def test_mismatched_temporal_years() -> None:
    """Verify mismatched historical years are flagged."""
    claim = "The event occurred in 2024."
    evidence = "The historical treaty was signed in 1998."
    result = validate_temporal_alignment(claim, evidence)

    assert result.is_temporally_valid is False
    assert result.status == "TEMPORAL_DISCREPANCY"


def test_unconstrained_claim_temporal() -> None:
    """Verify unconstrained claim passes temporal check."""
    claim = "Water boils at 100 degrees Celsius at standard atmospheric pressure."
    evidence = "The boiling point of water is 100C."
    result = validate_temporal_alignment(claim, evidence)

    assert result.is_temporally_valid is True
    assert result.status == "UNCONSTRAINED_TEMPORAL"
