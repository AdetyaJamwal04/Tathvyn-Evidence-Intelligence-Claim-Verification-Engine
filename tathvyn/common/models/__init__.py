"""VeriFact Core Domain Models Package."""

from tathvyn.common.models.claim import AtomicClaim, Claim, ClaimAnalysis
from tathvyn.common.models.conflict import Conflict
from tathvyn.common.models.evidence import (
    Evidence,
    EvidenceGraph,
    EvidenceSnapshot,
    EvidenceState,
)
from tathvyn.common.models.provenance import ProvenanceEdge, ProvenanceGroup
from tathvyn.common.models.research import (
    BudgetConsumption,
    ResearchAction,
    ResearchBudget,
    ResearchState,
    ResearchTask,
)
from tathvyn.common.models.source import Document, Passage, Source
from tathvyn.common.models.verdict import Citation, VerdictDecision, VerdictRecord

__all__ = [
    "AtomicClaim",
    "BudgetConsumption",
    "Citation",
    "Claim",
    "ClaimAnalysis",
    "Conflict",
    "Document",
    "Evidence",
    "EvidenceGraph",
    "EvidenceSnapshot",
    "EvidenceState",
    "Passage",
    "ProvenanceEdge",
    "ProvenanceGroup",
    "ResearchAction",
    "ResearchBudget",
    "ResearchState",
    "ResearchTask",
    "Source",
    "VerdictDecision",
    "VerdictRecord",
]
