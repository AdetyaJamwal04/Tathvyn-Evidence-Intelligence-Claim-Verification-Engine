"""Domain Models for Evidence Assessment, Graphs, and Snapshots."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tathvyn.common.enums import EvidenceRelationship


class Evidence(BaseModel):
    """A claim-relative empirical interpretation of a document passage."""

    evidence_id: UUID = Field(default_factory=uuid4)
    atomic_claim_id: UUID
    passage_id: UUID
    provenance_group_id: UUID | None = None
    relationship: EvidenceRelationship
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    entailment_score: float = Field(default=0.0, ge=0.0, le=1.0)
    contradiction_score: float = Field(default=0.0, ge=0.0, le=1.0)
    source_quality_score: float = Field(default=0.5, ge=0.0, le=1.0)
    independence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    temporal_validity_status: str = "VALID"
    assessment_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EvidenceState(BaseModel):
    """Aggregated epistemic state consumed by the Verdict Engine."""

    atomic_claim_id: UUID
    supporting_evidence: list[Evidence] = Field(default_factory=list)
    contradicting_evidence: list[Evidence] = Field(default_factory=list)
    context_evidence: list[Evidence] = Field(default_factory=list)
    coverage_score: float = Field(default=0.0, ge=0.0, le=1.0)
    temporal_validity: bool = True
    unresolved_conflict: bool = False


class EvidenceSnapshot(BaseModel):
    """An immutable record capturing the exact evidence state justifying a verdict."""

    snapshot_id: UUID = Field(default_factory=uuid4)
    claim_id: UUID
    evidence_ids: list[UUID] = Field(default_factory=list)
    provenance_group_ids: list[UUID] = Field(default_factory=list)
    policy_version: str = "standard_v1"
    snapshot_checksum: str = Field(
        ..., description="Deterministic SHA256 of sorted evidence IDs and policy"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EvidenceGraph(BaseModel):
    """In-memory typed graph of all claims, atomic claims, evidence, and provenance edges."""

    nodes: dict[str, list[dict[str, str]]] = Field(default_factory=dict)
    edges: list[dict[str, str]] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
