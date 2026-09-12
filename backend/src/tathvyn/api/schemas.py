"""Pydantic v2 Request, Response, and Error Schemas for VeriFact REST API."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tathvyn.common.enums import InternalVerdict, PublicVerdict, ResearchDepth


class CitationSchema(BaseModel):
    """Grounded citation schema serialized in API responses."""

    citation_id: int
    url: str
    source_name: str
    domain: str
    authority_class: str = "PRIMARY"
    supporting_passage: str


class ClaimVerificationRequest(BaseModel):
    """Request payload for synchronous claim verification."""

    claim: str = Field(
        ...,
        min_length=3,
        max_length=4000,
        description="Raw natural language claim text to verify.",
        examples=["Sweden joined NATO as its 32nd member state in March 2024."],
    )
    depth: ResearchDepth = Field(
        default=ResearchDepth.STANDARD,
        description="Verification depth profile (FAST: 0 loops, STANDARD: <=2 loops, DEEP: <=3 loops).",
    )
    request_id: UUID = Field(
        default_factory=uuid4,
        description="Optional client-generated tracking UUID.",
    )


class ClaimVerificationResponse(BaseModel):
    """Synchronous verification response payload."""

    request_id: UUID
    claim: str
    verdict: InternalVerdict
    public_label: PublicVerdict
    confidence: float
    evidence_sufficiency: float
    framing_concerns: bool
    stop_reason: str
    summary_text: str
    citations: list[CitationSchema] = Field(default_factory=list)
    latency_ms: float
    verified_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AsyncResearchJobRequest(BaseModel):
    """Request payload for asynchronous deep research dispatch."""

    claim: str = Field(
        ...,
        min_length=3,
        max_length=4000,
        description="Claim to dispatch for background deep research.",
    )
    depth: ResearchDepth = Field(
        default=ResearchDepth.DEEP,
        description="Verification depth profile.",
    )


class AsyncResearchJobResponse(BaseModel):
    """Immediate HTTP 202 response when research job is enqueued."""

    job_id: UUID
    status: str = "QUEUED"
    claim: str
    depth: ResearchDepth
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    polling_url: str


class ResearchJobStatusResponse(BaseModel):
    """Status polling response for asynchronous research jobs."""

    job_id: UUID
    status: str  # QUEUED, PROCESSING, COMPLETED, FAILED
    claim: str
    depth: ResearchDepth
    created_at: datetime
    updated_at: datetime
    result: ClaimVerificationResponse | None = None
    error: str | None = None


class HealthCheckResponse(BaseModel):
    """System health status and operational telemetry."""

    status: str = "healthy"
    version: str = "1.0.0"
    uptime_seconds: float
    database_connected: bool
    redis_connected: bool
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RFC7807ProblemDetails(BaseModel):
    """Standardized IETF RFC-7807 Problem Details error schema."""

    type: str
    title: str
    status: int
    detail: str
    instance: str
    error_code: str
    invalid_params: list[dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
