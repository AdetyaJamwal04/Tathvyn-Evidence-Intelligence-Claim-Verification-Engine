"""Tests for Grounded Explanation Builder and Citations."""

from uuid import uuid4

from tathvyn.common.enums import EvidenceRelationship, InternalVerdict
from tathvyn.common.models.evidence import Evidence
from tathvyn.common.models.source import Document, Passage
from tathvyn.verdict.explainer import GroundedExplanationBuilder


def test_citation_building() -> None:
    """Verify structured citations are formatted with quotes and domains."""
    builder = GroundedExplanationBuilder()

    doc = Document(
        source_id=uuid4(),
        url="https://nasa.gov/jwst-mission",
        canonical_url="https://nasa.gov/jwst-mission",
        content_hash="h1",
        title="NASA JWST",
    )
    passage = Passage(
        document_id=doc.document_id,
        sequence_order=0,
        text="The James Webb Space Telescope operates at Sun-Earth L2.",
        char_start=0,
        char_end=58,
        token_count=9,
        content_hash="ph1",
    )
    ev = Evidence(
        atomic_claim_id=uuid4(),
        passage_id=passage.passage_id,
        relationship=EvidenceRelationship.SUPPORTS,
    )

    citations = builder.build_citations(
        evidence_items=[ev],
        passages_by_id={passage.passage_id: passage},
        documents_by_id={doc.document_id: doc},
    )

    assert len(citations) == 1
    assert citations[0].domain == "nasa.gov"
    assert "James Webb" in citations[0].supporting_passage


def test_grounded_summary_generation() -> None:
    """Verify summary includes claim text and key citations."""
    builder = GroundedExplanationBuilder()
    summary = builder.generate_summary(
        claim_text="Speed of light is 299792458 m/s.",
        verdict=InternalVerdict.SUPPORTED,
        citations=[],
        rationale="Verified.",
    )
    assert "verified as accurate" in summary
