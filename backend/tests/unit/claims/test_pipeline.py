"""Tests for End-to-End ClaimIntelligencePipeline."""

from uuid import uuid4

import pytest

from tathvyn.claims.pipeline import ClaimIntelligencePipeline
from tathvyn.common.enums import ClaimType, ClaimVerifiability
from tathvyn.common.exceptions import UnsupportedLanguageError


def test_pipeline_atomic_claim_flow() -> None:
    """Verify end-to-end processing of a factual numerical claim."""
    pipeline = ClaimIntelligencePipeline()
    req_id = uuid4()
    raw = "Is it true that India's real GDP grew by 8.2% in FY 2023-24?"

    analysis = pipeline.analyze(raw, request_id=req_id)

    assert analysis.claim.request_id == req_id
    assert analysis.claim.language_code == "en"
    assert analysis.claim.primary_type == ClaimType.NUMERICAL
    assert analysis.claim.domain == "ECONOMICS"
    assert analysis.claim.verifiability == ClaimVerifiability.VERIFIABLE
    assert len(analysis.atomic_claims) >= 1
    assert len(analysis.extracted_temporal_intervals) >= 1


def test_pipeline_non_english_rejection() -> None:
    """Verify pipeline rejects non-English input immediately."""
    pipeline = ClaimIntelligencePipeline()
    with pytest.raises(UnsupportedLanguageError):
        pipeline.analyze("El telescopio espacial James Webb opera en el punto L2.")


def test_pipeline_unverifiable_claim_flow() -> None:
    """Verify subjective opinion produces UNVERIFIABLE claim analysis."""
    pipeline = ClaimIntelligencePipeline()
    analysis = pipeline.analyze(
        "Modern contemporary art is culturally inferior to Renaissance oil paintings."
    )

    assert analysis.claim.verifiability == ClaimVerifiability.UNVERIFIABLE
    assert analysis.claim.primary_type == ClaimType.OPINION
