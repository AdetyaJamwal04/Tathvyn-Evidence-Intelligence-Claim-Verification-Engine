"""
Core Domain Models for Claims and Propositions.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tathvyn.common.enums import (
    AtomicClaimVerdict,
    ClaimComplexity,
    ClaimType,
    ClaimVerifiability,
    Materiality,
)


class AtomicClaim(BaseModel):
    """An independently verifiable atomic proposition derived from a parent claim."""

    atomic_claim_id: UUID = Field(default_factory=uuid4)
    claim_id: UUID
    sequence_order: int = 0
    text: str = Field(..., min_length=3, description="The normalized atomic proposition text")
    is_atomic: bool = True
    decomposition_depth: int = Field(
        default=1, le=1, description="Capped at 1 for terminal atomic claims"
    )
    materiality: Materiality = Materiality.MATERIAL
    entities: list[str] = Field(default_factory=list)
    temporal_scope: dict[str, str] = Field(default_factory=dict)
    status: AtomicClaimVerdict = AtomicClaimVerdict.INSUFFICIENT
    is_comparative: bool = False
    is_causal: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Claim(BaseModel):
    """A claim being evaluated by the verification system."""

    claim_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    raw_text: str = Field(..., min_length=5)
    normalized_text: str = Field(..., min_length=5)
    language_code: str = "en"
    primary_type: ClaimType = ClaimType.FACTUAL
    secondary_types: list[ClaimType] = Field(default_factory=list)
    domain: str = "GENERAL"
    complexity: ClaimComplexity = ClaimComplexity.MODERATE
    verifiability: ClaimVerifiability = ClaimVerifiability.VERIFIABLE
    is_atomic: bool = False
    content_hash: str = Field(..., description="SHA256 of normalized claim text")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ClaimAnalysis(BaseModel):
    """The structured output of the Claim Intelligence stage."""

    claim: Claim
    atomic_claims: list[AtomicClaim]
    extracted_entities: list[dict[str, str]] = Field(default_factory=list)
    extracted_temporal_intervals: list[dict[str, str]] = Field(default_factory=list)
    verifiability_reasoning: str = ""
