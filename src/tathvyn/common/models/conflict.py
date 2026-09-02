"""Domain Models for Disagreements and Conflicts between Evidence Items."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tathvyn.common.enums import ConflictResolutionStatus, ConflictSeverity, ConflictType


class Conflict(BaseModel):
    """An identified empirical or definitional contradiction between evidence items."""

    conflict_id: UUID = Field(default_factory=uuid4)
    atomic_claim_id: UUID
    evidence_id_a: UUID
    evidence_id_b: UUID
    conflict_type: ConflictType = ConflictType.DIRECT_CONTRADICTION
    severity: ConflictSeverity = ConflictSeverity.MAJOR
    resolution_status: ConflictResolutionStatus = ConflictResolutionStatus.UNRESOLVED
    resolution_rationale: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
