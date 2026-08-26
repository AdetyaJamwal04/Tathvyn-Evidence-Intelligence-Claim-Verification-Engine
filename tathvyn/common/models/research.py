"""Domain Models for Research Orchestration and Control Plane State."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tathvyn.common.enums import (
    ResearchActionType,
    ResearchObjective,
    ResearchStateStatus,
    ResearchStopReason,
)
from tathvyn.common.models.claim import AtomicClaim, Claim
from tathvyn.common.models.conflict import Conflict
from tathvyn.common.models.evidence import EvidenceGraph
from tathvyn.common.models.provenance import ProvenanceGroup


class ResearchBudget(BaseModel):
    """Resource constraints for an adaptive research session."""

    max_iterations: int = 5
    max_search_queries: int = 12
    max_document_fetches: int = 8
    max_llm_tokens: int = 16000
    max_wall_time_seconds: float = 25.0
    max_cost_usd: Decimal = Decimal("0.05")


class BudgetConsumption(BaseModel):
    """Accumulated resource expenditure for an adaptive research session."""

    iterations_used: int = 0
    search_queries_used: int = 0
    documents_fetched: int = 0
    llm_tokens_used: int = 0
    elapsed_seconds: float = 0.0
    estimated_cost_usd: Decimal = Decimal("0.00")


class ResearchAction(BaseModel):
    """A discrete research task dispatched by the orchestrator."""

    action_id: UUID = Field(default_factory=uuid4)
    action_type: ResearchActionType
    target_atomic_claim_id: UUID | None = None
    query_text: str | None = None
    target_url: str | None = None
    rationale: str = ""
    estimated_cost: Decimal = Decimal("0.001")


class ResearchTask(BaseModel):
    """A tracked investigative task in the research queue."""

    task_id: UUID = Field(default_factory=uuid4)
    atomic_claim_id: UUID
    objective: ResearchObjective
    priority: float = 1.0
    expected_value: float = 0.5
    status: str = "PENDING"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ResearchState(BaseModel):
    """Full operational and epistemic context of a research session."""

    verification_id: UUID = Field(default_factory=uuid4)
    claim: Claim
    atomic_claims: list[AtomicClaim] = Field(default_factory=list)
    status: ResearchStateStatus = ResearchStateStatus.RECEIVED
    current_iteration: int = 0
    evidence_graph: EvidenceGraph = Field(default_factory=EvidenceGraph)
    provenance_clusters: list[ProvenanceGroup] = Field(default_factory=list)
    unresolved_conflicts: list[Conflict] = Field(default_factory=list)
    pending_actions: list[ResearchAction] = Field(default_factory=list)
    budget: ResearchBudget = Field(default_factory=ResearchBudget)
    budget_consumed: BudgetConsumption = Field(default_factory=BudgetConsumption)
    stop_reason: ResearchStopReason | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
