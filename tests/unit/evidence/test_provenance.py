"""Tests for Provenance Clustering and Independence Scoring."""

from uuid import uuid4

from tathvyn.common.enums import EvidenceRelationship
from tathvyn.common.models.evidence import Evidence
from tathvyn.common.models.source import Document, Passage
from tathvyn.evidence.provenance import ProvenanceClusterer


def test_domain_clustering_and_independence_discounting() -> None:
    """Verify documents from same domain are grouped and discounted."""
    clusterer = ProvenanceClusterer()

    doc1 = Document(
        source_id=uuid4(),
        url="https://reuters.com/article1",
        canonical_url="https://reuters.com/article1",
        content_hash="h1",
    )
    doc2 = Document(
        source_id=uuid4(),
        url="https://reuters.com/article2",
        canonical_url="https://reuters.com/article2",
        content_hash="h2",
    )

    p1 = Passage(
        document_id=doc1.document_id,
        sequence_order=0,
        text="First passage text from Reuters.",
        char_start=0,
        char_end=31,
        token_count=5,
        content_hash="ph1",
    )
    p2 = Passage(
        document_id=doc2.document_id,
        sequence_order=0,
        text="Second passage text from Reuters.",
        char_start=0,
        char_end=32,
        token_count=5,
        content_hash="ph2",
    )

    ev1 = Evidence(
        atomic_claim_id=uuid4(),
        passage_id=p1.passage_id,
        relationship=EvidenceRelationship.SUPPORTS,
    )
    ev2 = Evidence(
        atomic_claim_id=uuid4(),
        passage_id=p2.passage_id,
        relationship=EvidenceRelationship.SUPPORTS,
    )

    passages_map = {p1.passage_id: p1, p2.passage_id: p2}
    docs_map = {doc1.document_id: doc1, doc2.document_id: doc2}

    clusters, updated_ev = clusterer.cluster_evidence([ev1, ev2], passages_map, docs_map)

    assert len(clusters) == 1
    assert len(clusters[0].member_evidence_ids) == 2
    assert updated_ev[0].independence_score == 1.0
    assert updated_ev[1].independence_score == 0.25  # Discounted for duplicate domain
