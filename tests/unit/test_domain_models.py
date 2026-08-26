"""Tests for Pydantic v2 Domain Models Validation and Serialization."""

import hashlib
from uuid import uuid4

import pytest
from pydantic import ValidationError

from tathvyn.common.enums import (
    AuthorityClass,
    ClaimType,
    InternalVerdict,
    Materiality,
    PublicVerdict,
    SourceType,
)
from tathvyn.common.models import (
    AtomicClaim,
    Citation,
    Claim,
    Document,
    Passage,
    Source,
    VerdictDecision,
)


def test_claim_model_creation() -> None:
    """Verify valid Claim instantiation and hashing."""
    req_id = uuid4()
    text = "India's GDP grew by 8.2% in fiscal year 2023-24."
    c_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

    claim = Claim(
        request_id=req_id,
        raw_text=text,
        normalized_text=text,
        primary_type=ClaimType.NUMERICAL,
        secondary_types=[ClaimType.FACTUAL, ClaimType.FINANCIAL],
        domain="ECONOMICS",
        content_hash=c_hash,
    )

    assert claim.primary_type == ClaimType.NUMERICAL
    assert claim.language_code == "en"
    assert claim.content_hash == c_hash

    # JSON roundtrip
    json_str = claim.model_dump_json()
    reconstructed = Claim.model_validate_json(json_str)
    assert reconstructed.claim_id == claim.claim_id


def test_atomic_claim_model() -> None:
    """Verify AtomicClaim validation and depth constraints."""
    claim_id = uuid4()
    ac = AtomicClaim(
        claim_id=claim_id,
        text="India real GDP grew 8.2%.",
        materiality=Materiality.CRITICAL,
        decomposition_depth=1,
    )
    assert ac.is_atomic is True
    assert ac.decomposition_depth <= 1

    # Capped depth test
    with pytest.raises(ValidationError):
        AtomicClaim(claim_id=claim_id, text="Too deep", decomposition_depth=2)


def test_source_and_passage_models() -> None:
    """Verify Source, Document, and Passage schema hierarchy."""
    src = Source(
        canonical_domain="mospi.gov.in",
        publisher_name="Ministry of Statistics",
        source_type=SourceType.GOVERNMENT,
        authority_class=AuthorityClass.PRIMARY,
        domain_authority_score=0.98,
    )

    doc = Document(
        source_id=src.source_id,
        url="https://mospi.gov.in/gdp-report",
        canonical_url="https://mospi.gov.in/gdp-report",
        content_hash="mock_hash",
        title="GDP Estimates FY24",
    )

    passage = Passage(
        document_id=doc.document_id,
        sequence_order=1,
        text="The growth in real GDP during 2023-24 is estimated at 8.2 per cent.",
        char_start=0,
        char_end=68,
        token_count=15,
        content_hash="p_hash",
        embedding=[0.1] * 384,
    )

    assert passage.embedding is not None
    assert len(passage.embedding) == 384
    assert passage.document_id == doc.document_id


def test_verdict_decision_model() -> None:
    """Verify VerdictDecision and Citation models."""
    citation = Citation(
        citation_id=1,
        source_name="MoSPI",
        domain="mospi.gov.in",
        url="https://mospi.gov.in/gdp-report",
        authority_class="PRIMARY",
        supporting_passage="Real GDP growth estimated at 8.2%.",
    )

    decision = VerdictDecision(
        verdict=InternalVerdict.SUPPORTED,
        public_label=PublicVerdict.LIKELY_TRUE,
        confidence=0.94,
        evidence_sufficiency=0.91,
        stop_reason="SUFFICIENT_EVIDENCE",
        summary_text="Verified by official MoSPI release.",
        citations=[citation],
    )

    assert decision.confidence == 0.94
    assert len(decision.citations) == 1
    assert decision.public_label == PublicVerdict.LIKELY_TRUE
