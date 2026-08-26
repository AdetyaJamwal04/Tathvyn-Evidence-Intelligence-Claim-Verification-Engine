"""SQLAlchemy ORM Models for Sources, Documents, and Passages."""

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tathvyn.storage.database import Base

if TYPE_CHECKING:
    from tathvyn.storage.models.evidence_orm import EvidenceORM


class SourceORM(Base):
    """Database entity representing an information publisher or originating domain."""

    __tablename__ = "sources"

    source_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    canonical_domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    publisher_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, default="UNKNOWN")
    authority_class: Mapped[str] = mapped_column(String(16), nullable=False, default="UNKNOWN")
    domain_authority_score: Mapped[float] = mapped_column(Float, default=0.5)
    country_code: Mapped[str | None] = mapped_column(String(4), nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    documents: Mapped[list["DocumentORM"]] = relationship(
        "DocumentORM", back_populates="source", cascade="all, delete-orphan"
    )


class DocumentORM(Base):
    """Database entity representing a retrieved web document."""

    __tablename__ = "documents"
    __table_args__ = (UniqueConstraint("canonical_url", "content_hash", name="uq_doc_url_hash"),)

    document_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    source_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("sources.source_id"), nullable=False
    )
    url: Mapped[str] = mapped_column(String, nullable=False)
    canonical_url: Mapped[str] = mapped_column(String, nullable=False, index=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    http_status: Mapped[int] = mapped_column(Integer, default=200)
    storage_uri: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    source: Mapped["SourceORM"] = relationship("SourceORM", back_populates="documents")
    passages: Mapped[list["PassageORM"]] = relationship(
        "PassageORM", back_populates="document", cascade="all, delete-orphan"
    )


class PassageORM(Base):
    """Database entity representing an individual segmented passage with pgvector embedding."""

    __tablename__ = "passages"

    passage_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("documents.document_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    char_start: Mapped[int] = mapped_column(Integer, nullable=False)
    char_end: Mapped[int] = mapped_column(Integer, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding = mapped_column(Vector(384), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    document: Mapped["DocumentORM"] = relationship("DocumentORM", back_populates="passages")
    evidence_items: Mapped[list["EvidenceORM"]] = relationship(
        "EvidenceORM", back_populates="passage"
    )
