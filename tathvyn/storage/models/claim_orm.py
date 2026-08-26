"""SQLAlchemy ORM Models for Claims and Atomic Claims."""

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tathvyn.storage.database import Base

if TYPE_CHECKING:
    from tathvyn.storage.models.evidence_orm import (
        ConflictORM,
        EvidenceORM,
        EvidenceSnapshotORM,
    )
    from tathvyn.storage.models.request_orm import VerificationRequestORM


class ClaimORM(Base):
    """Database entity representing a normalized verification claim."""

    __tablename__ = "claims"

    claim_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("verification_requests.request_id", ondelete="CASCADE"),
        nullable=False,
    )
    raw_text: Mapped[str] = mapped_column(String, nullable=False)
    normalized_text: Mapped[str] = mapped_column(String, nullable=False)
    language_code: Mapped[str] = mapped_column(String(8), nullable=False, default="en")
    primary_type: Mapped[str] = mapped_column(String(32), nullable=False)
    secondary_types: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    domain: Mapped[str] = mapped_column(String(32), nullable=False, default="GENERAL")
    complexity: Mapped[str] = mapped_column(String(16), nullable=False, default="MODERATE")
    is_atomic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    request: Mapped["VerificationRequestORM"] = relationship(
        "VerificationRequestORM", back_populates="claims"
    )
    atomic_claims: Mapped[list["AtomicClaimORM"]] = relationship(
        "AtomicClaimORM", back_populates="claim", cascade="all, delete-orphan"
    )
    snapshots: Mapped[list["EvidenceSnapshotORM"]] = relationship(
        "EvidenceSnapshotORM", back_populates="claim", cascade="all, delete-orphan"
    )


class AtomicClaimORM(Base):
    """Database entity representing an atomic claim proposition."""

    __tablename__ = "atomic_claims"

    atomic_claim_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    claim_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("claims.claim_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    text: Mapped[str] = mapped_column(String, nullable=False)
    is_atomic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    decomposition_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    materiality: Mapped[str] = mapped_column(String(16), nullable=False, default="MATERIAL")
    entities: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    temporal_scope: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="UNRESEARCHED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    claim: Mapped["ClaimORM"] = relationship("ClaimORM", back_populates="atomic_claims")
    evidence_items: Mapped[list["EvidenceORM"]] = relationship(
        "EvidenceORM", back_populates="atomic_claim", cascade="all, delete-orphan"
    )
    conflicts: Mapped[list["ConflictORM"]] = relationship(
        "ConflictORM", back_populates="atomic_claim", cascade="all, delete-orphan"
    )
