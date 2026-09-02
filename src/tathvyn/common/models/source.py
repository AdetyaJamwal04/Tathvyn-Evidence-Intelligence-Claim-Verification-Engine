"""Core Domain Models for Information Sources, Documents, and Passages."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tathvyn.common.enums import AuthorityClass, SourceType


class Source(BaseModel):
    """An originating publisher or institutional entity."""

    source_id: UUID = Field(default_factory=uuid4)
    canonical_domain: str = Field(..., description="e.g. 'mospi.gov.in' or 'reuters.com'")
    publisher_name: str | None = None
    source_type: SourceType = SourceType.UNKNOWN
    authority_class: AuthorityClass = AuthorityClass.UNKNOWN
    domain_authority_score: float = Field(default=0.5, ge=0.0, le=1.0)
    country_code: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Document(BaseModel):
    """A retrievable web page or publication version."""

    document_id: UUID = Field(default_factory=uuid4)
    source_id: UUID
    url: str
    canonical_url: str
    content_hash: str = Field(..., description="SHA256 of extracted textual content")
    title: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    http_status: int = 200
    storage_uri: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Passage(BaseModel):
    """An individual text segment extracted from a document."""

    passage_id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    sequence_order: int
    text: str = Field(..., min_length=10)
    char_start: int
    char_end: int
    token_count: int
    content_hash: str = Field(..., description="SHA256 of passage text")
    embedding: list[float] | None = None  # 384-dimensional dense vector
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
