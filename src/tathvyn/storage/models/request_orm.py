"""SQLAlchemy ORM Model for Verification Requests."""

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tathvyn.storage.database import Base

if TYPE_CHECKING:
    from tathvyn.storage.models.claim_orm import ClaimORM


class VerificationRequestORM(Base):
    """Database entity representing an API verification request."""

    __tablename__ = "verification_requests"

    request_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, default="default")
    raw_input: Mapped[str] = mapped_column(String, nullable=False)
    mode: Mapped[str] = mapped_column(String(16), nullable=False, default="STANDARD")
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="QUEUED")
    client_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    claims: Mapped[list["ClaimORM"]] = relationship(
        "ClaimORM", back_populates="request", cascade="all, delete-orphan"
    )
