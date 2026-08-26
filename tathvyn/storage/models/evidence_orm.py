"""SQLAlchemy ORM Models for Evidence, Provenance, Conflicts, and Snapshots."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as sa_relationship

from tathvyn.storage.database import Base

if TYPE_CHECKING:
    from tathvyn.storage.models.claim_orm import AtomicClaimORM, ClaimORM
    from tathvyn.storage.models.source_orm import PassageORM, SourceORM
    from tathvyn.storage.models.verdict_orm import VerdictORM


class ProvenanceGroupORM(Base):
    """Database entity representing a cluster of documents with a common origin."""

    __tablename__ = "provenance_groups"

    provenance_group_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    root_source_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("sources.source_id"), nullable=True
    )
    detection_method: Mapped[str] = mapped_column(String(32), nullable=False)
    cluster_confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    source: Mapped["SourceORM | None"] = sa_relationship("SourceORM")
    evidence_items: Mapped[list["EvidenceORM"]] = sa_relationship(
        "EvidenceORM", back_populates="provenance_group"
    )


class EvidenceORM(Base):
    """Database entity representing an atomic-claim-relative evidence assessment."""

    __tablename__ = "evidence"

    evidence_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    atomic_claim_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("atomic_claims.atomic_claim_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    passage_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("passages.passage_id"), nullable=False
    )
    provenance_group_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("provenance_groups.provenance_group_id"), nullable=True
    )
    relationship: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    entailment_score: Mapped[float] = mapped_column(Float, default=0.0)
    contradiction_score: Mapped[float] = mapped_column(Float, default=0.0)
    source_quality_score: Mapped[float] = mapped_column(Float, default=0.5)
    independence_score: Mapped[float] = mapped_column(Float, default=1.0)
    temporal_validity_status: Mapped[str] = mapped_column(String(24), default="VALID")
    assessment_version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    atomic_claim: Mapped["AtomicClaimORM"] = sa_relationship(
        "AtomicClaimORM", back_populates="evidence_items"
    )
    passage: Mapped["PassageORM"] = sa_relationship("PassageORM", back_populates="evidence_items")
    provenance_group: Mapped["ProvenanceGroupORM | None"] = sa_relationship(
        "ProvenanceGroupORM", back_populates="evidence_items"
    )


class ConflictORM(Base):
    """Database entity representing an unresolved or resolved evidence contradiction."""

    __tablename__ = "conflicts"

    conflict_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    atomic_claim_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("atomic_claims.atomic_claim_id", ondelete="CASCADE"),
        nullable=False,
    )
    evidence_id_a: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("evidence.evidence_id"), nullable=False
    )
    evidence_id_b: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("evidence.evidence_id"), nullable=False
    )
    conflict_type: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default="MAJOR")
    resolution_status: Mapped[str] = mapped_column(String(32), nullable=False, default="UNRESOLVED")
    resolution_rationale: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    atomic_claim: Mapped["AtomicClaimORM"] = sa_relationship(
        "AtomicClaimORM", back_populates="conflicts"
    )


class EvidenceSnapshotORM(Base):
    """Immutable database snapshot capturing the exact evidence IDs used for a verdict."""

    __tablename__ = "evidence_snapshots"

    snapshot_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    claim_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("claims.claim_id", ondelete="CASCADE"), nullable=False
    )
    evidence_ids: Mapped[list[UUID]] = mapped_column(ARRAY(PG_UUID(as_uuid=True)), nullable=False)
    provenance_group_ids: Mapped[list[UUID]] = mapped_column(
        ARRAY(PG_UUID(as_uuid=True)), nullable=False
    )
    policy_version: Mapped[str] = mapped_column(String(32), nullable=False)
    snapshot_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    claim: Mapped["ClaimORM"] = sa_relationship("ClaimORM", back_populates="snapshots")
    verdict: Mapped["VerdictORM | None"] = sa_relationship(
        "VerdictORM", back_populates="snapshot", uselist=False
    )
