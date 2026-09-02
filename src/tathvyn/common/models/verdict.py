"""Domain Models for Verdicts, Decisions, and Citations."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tathvyn.common.enums import InternalVerdict, PublicVerdict


class Citation(BaseModel):
    """A user-facing citation linking a factual assertion to a specific source passage."""

    citation_id: int
    source_name: str
    domain: str
    url: str
    authority_class: str
    publication_date: datetime | None = None
    supporting_passage: str


class VerdictDecision(BaseModel):
    """Structured decision object produced by the Verdict Engine."""

    verdict: InternalVerdict
    public_label: PublicVerdict
    framing_concerns: bool = False
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Empirically calibrated confidence score"
    )
    evidence_sufficiency: float = Field(..., ge=0.0, le=1.0)
    stop_reason: str
    summary_text: str
    citations: list[Citation] = Field(default_factory=list)
    supporting_evidence_ids: list[UUID] = Field(default_factory=list)
    contradicting_evidence_ids: list[UUID] = Field(default_factory=list)
    unresolved_atomic_claim_ids: list[UUID] = Field(default_factory=list)


class VerdictRecord(BaseModel):
    """Permanent database representation of a verification verdict."""

    verdict_id: UUID = Field(default_factory=uuid4)
    claim_id: UUID
    snapshot_id: UUID
    verdict: InternalVerdict
    public_label: PublicVerdict
    framing_concerns: bool = False
    confidence: float
    evidence_sufficiency: float
    stop_reason: str
    summary_text: str
    citations: list[Citation]
    engine_version: str = "1.0.0"
    calibration_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
