"""Domain Models for Provenance Clustering and Graph Edges."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tathvyn.common.enums import ProvenanceDetectionMethod, ProvenanceRelationship


class ProvenanceGroup(BaseModel):
    """A cluster of documents and evidence originating from a common underlying source."""

    provenance_group_id: UUID = Field(default_factory=uuid4)
    root_source_id: UUID | None = None
    member_evidence_ids: list[UUID] = Field(default_factory=list)
    detection_method: ProvenanceDetectionMethod = ProvenanceDetectionMethod.URL_DOMAIN_CLUSTERING
    cluster_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProvenanceEdge(BaseModel):
    """A directed derivation or citation link between two documents."""

    edge_id: UUID = Field(default_factory=uuid4)
    source_doc_id: UUID
    target_doc_id: UUID
    relationship: ProvenanceRelationship
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    detection_method: ProvenanceDetectionMethod
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
