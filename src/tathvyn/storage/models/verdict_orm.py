"""SQLAlchemy ORM Model for Verification Verdicts."""

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tathvyn.storage.database import Base

if TYPE_CHECKING:
    from tathvyn.storage.models.evidence_orm import EvidenceSnapshotORM


class VerdictORM(Base):
    """Database entity representing a permanently recorded verification verdict."""

    __tablename__ = "verdicts"

    verdict_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    claim_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("claims.claim_id", ondelete="CASCADE"), nullable=False
    )
    snapshot_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("evidence_snapshots.snapshot_id"),
        nullable=False,
        unique=True,
    )
    verdict: Mapped[str] = mapped_column(String(32), nullable=False)
    public_label: Mapped[str] = mapped_column(String(32), nullable=False)
    framing_concerns: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_sufficiency: Mapped[float] = mapped_column(Float, nullable=False)
    stop_reason: Mapped[str] = mapped_column(String(32), nullable=False)
    summary_text: Mapped[str] = mapped_column(String, nullable=False)
    citations: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    engine_version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    calibration_version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    snapshot: Mapped["EvidenceSnapshotORM"] = relationship(
        "EvidenceSnapshotORM", back_populates="verdict"
    )
