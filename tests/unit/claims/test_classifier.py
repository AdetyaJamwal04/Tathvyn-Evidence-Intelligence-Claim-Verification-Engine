"""Tests for Multi-Label Semantic Claim Classifier."""

from tathvyn.claims.classifier import classify_claim
from tathvyn.common.enums import ClaimType, ClaimVerifiability


def test_numerical_and_financial_claim() -> None:
    """Verify numerical and financial taxonomy detection."""
    claim = "India's real GDP grew by 8.2% in financial year 2023-24 according to MoSPI."
    result = classify_claim(claim)
    assert result.primary_type == ClaimType.NUMERICAL
    assert result.domain == "ECONOMICS"
    assert result.verifiability == ClaimVerifiability.VERIFIABLE


def test_attribution_claim() -> None:
    """Verify quote / speech attribution classification."""
    claim = "Winston Churchill said: 'If you're going through hell, keep going.'"
    result = classify_claim(claim)
    assert result.primary_type == ClaimType.ATTRIBUTION
    assert result.verifiability == ClaimVerifiability.VERIFIABLE


def test_normative_and_opinion_unverifiability() -> None:
    """Verify subjective opinions and moral judgments are classified as UNVERIFIABLE."""
    # Opinion
    opinion = "Vanilla ice cream tastes significantly better than chocolate ice cream."
    res_op = classify_claim(opinion)
    assert res_op.primary_type == ClaimType.OPINION
    assert res_op.verifiability == ClaimVerifiability.UNVERIFIABLE

    # Normative
    normative = "The government should immediately lower corporate tax rates to zero."
    res_norm = classify_claim(normative)
    assert res_norm.primary_type == ClaimType.NORMATIVE
    assert res_norm.verifiability == ClaimVerifiability.UNVERIFIABLE
