"""Tests for SQLAlchemy ORM Models and Database Setup."""

from tathvyn.storage.database import get_engine, get_session_factory
from tathvyn.storage.models import (
    AtomicClaimORM,
    ClaimORM,
    ConflictORM,
    DocumentORM,
    EvidenceORM,
    EvidenceSnapshotORM,
    PassageORM,
    ProvenanceGroupORM,
    SourceORM,
    VerdictORM,
    VerificationRequestORM,
)
from tathvyn.storage.redis_client import get_redis_client, get_redis_pool


def test_orm_models_instantiation() -> None:
    """Verify ORM model classes and relationships can be instantiated."""
    req = VerificationRequestORM(raw_input="Test input", mode="FAST", status="QUEUED")
    assert req.mode == "FAST"
    assert req.status == "QUEUED"

    claim = ClaimORM(
        request_id=req.request_id,
        raw_text="Test raw",
        normalized_text="Test norm",
        primary_type="FACTUAL",
        content_hash="test_hash",
        language_code="en",
    )
    assert claim.language_code == "en"

    atomic = AtomicClaimORM(claim_id=claim.claim_id, text="Atomic sub-claim", is_atomic=True)
    assert atomic.is_atomic is True

    src = SourceORM(canonical_domain="reuters.com", source_type="NEWS_ORGANIZATION")
    doc = DocumentORM(
        source_id=src.source_id,
        url="https://reuters.com",
        canonical_url="https://reuters.com",
        content_hash="h1",
    )
    passage = PassageORM(
        document_id=doc.document_id,
        sequence_order=1,
        text="Passage text",
        char_start=0,
        char_end=12,
        token_count=2,
        content_hash="p1",
    )

    prov = ProvenanceGroupORM(detection_method="URL_DOMAIN_CLUSTERING")
    evidence = EvidenceORM(
        atomic_claim_id=atomic.atomic_claim_id,
        passage_id=passage.passage_id,
        relationship="SUPPORTS",
    )

    conflict = ConflictORM(
        atomic_claim_id=atomic.atomic_claim_id,
        evidence_id_a=evidence.evidence_id,
        evidence_id_b=evidence.evidence_id,
        conflict_type="DIRECT_CONTRADICTION",
    )
    assert conflict.conflict_type == "DIRECT_CONTRADICTION"

    snapshot = EvidenceSnapshotORM(
        claim_id=claim.claim_id,
        evidence_ids=[evidence.evidence_id],
        provenance_group_ids=[prov.provenance_group_id],
        policy_version="standard_v1",
        snapshot_checksum="sha256_checksum",
    )

    verdict = VerdictORM(
        claim_id=claim.claim_id,
        snapshot_id=snapshot.snapshot_id,
        verdict="SUPPORTED",
        public_label="LIKELY TRUE",
        confidence=0.95,
        evidence_sufficiency=0.90,
        stop_reason="SUFFICIENT_EVIDENCE",
        summary_text="Grounded summary",
    )

    assert verdict.public_label == "LIKELY TRUE"
    assert len(snapshot.evidence_ids) == 1


def test_database_and_redis_factories() -> None:
    """Verify database and redis engine/pool factories initialize."""
    engine = get_engine()
    assert engine is not None
    factory = get_session_factory()
    assert factory is not None

    pool = get_redis_pool()
    assert pool is not None
    client = get_redis_client()
    assert client is not None
