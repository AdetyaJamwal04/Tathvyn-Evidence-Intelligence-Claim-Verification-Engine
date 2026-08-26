"""Tests for Numerical Consistency and Tolerance Validator."""

from tathvyn.evidence.validators.numerical_validator import validate_numerical_consistency


def test_matching_numerical_values() -> None:
    """Verify exact and within-tolerance numerical values are validated."""
    claim = "India's GDP grew by 8.2% in FY24."
    evidence = "According to MoSPI, real GDP growth is estimated at 8.2 per cent for 2023-24."
    result = validate_numerical_consistency(claim, evidence, relative_tolerance=0.05)

    assert result.is_compatible is True
    assert result.validation_status == "VALID"
    assert result.discrepancy_ratio == 0.0


def test_mismatched_numerical_values() -> None:
    """Verify divergent numbers beyond tolerance fail validation."""
    claim = "Tesla delivered 2.5 million vehicles globally in 2023."
    evidence = "Tesla announced global deliveries of 1.81 million vehicles in 2023."
    result = validate_numerical_consistency(claim, evidence, relative_tolerance=0.05)

    assert result.is_compatible is False
    assert result.validation_status == "NUMERICAL_MISMATCH"
    assert result.discrepancy_ratio > 0.10


def test_no_numerical_assertions() -> None:
    """Verify claims without numbers pass validation."""
    claim = "The Eiffel Tower is located in Paris."
    evidence = "Paris is home to the Eiffel Tower."
    result = validate_numerical_consistency(claim, evidence)

    assert result.is_compatible is True
    assert result.validation_status == "NO_NUMERICAL_ASSERTION"
