"""Adaptive Research Loop Controller.

Evaluates evidence convergence and budget status across iterations, determining
whether to TERMINATE, REFINE_SEARCH, or RESOLVE_CONFLICT.
"""

from typing import NamedTuple
from uuid import UUID

from tathvyn.common.enums import ResearchLoopDecision
from tathvyn.common.models.conflict import Conflict
from tathvyn.common.models.evidence import EvidenceState
from tathvyn.orchestration.budget import BudgetTracker


class LoopDecisionResult(NamedTuple):
    """Decision outcome of the adaptive loop evaluation."""

    decision: ResearchLoopDecision
    rationale: str
    unresolved_atomic_claim_ids: list[UUID]


class AdaptiveLoopController:
    """Decides research iteration transitions based on evidence sufficiency and budget constraints."""

    def evaluate_loop_state(
        self,
        evidence_states: list[EvidenceState],
        conflicts: list[Conflict],
        budget_tracker: BudgetTracker,
    ) -> LoopDecisionResult:
        """Determine next action in the research cycle.

        Args:
            evidence_states: Evaluated evidence states for each atomic claim proposition.
            conflicts: Detected evidence conflicts.
            budget_tracker: Active execution budget tracker.

        Returns:
            LoopDecisionResult: Decision (TERMINATE, REFINE_SEARCH, RESOLVE_CONFLICT) and rationale.
        """
        # 1. Check budget limits first
        if not budget_tracker.can_execute_iteration():
            return LoopDecisionResult(
                decision=ResearchLoopDecision.TERMINATE,
                rationale=(
                    f"Iteration or budget limit reached (completed={budget_tracker.iterations_completed}, "
                    f"queries={budget_tracker.queries_consumed}, elapsed={budget_tracker.elapsed_seconds:.1f}s)."
                ),
                unresolved_atomic_claim_ids=[],
            )

        # 2. Check for unresolved direct empirical conflicts
        unresolved_conflicts = [c for c in conflicts if c.resolution_status.value == "UNRESOLVED"]
        if unresolved_conflicts:
            conflict_claim_ids = list({c.atomic_claim_id for c in unresolved_conflicts})
            return LoopDecisionResult(
                decision=ResearchLoopDecision.RESOLVE_CONFLICT,
                rationale=f"Detected {len(unresolved_conflicts)} unresolved empirical conflicts. Formulating targeted primary-source queries.",
                unresolved_atomic_claim_ids=conflict_claim_ids,
            )

        # 3. Check for atomic claims with low evidence coverage / insufficiency
        unresolved_ids = [
            st.atomic_claim_id
            for st in evidence_states
            if st.coverage_score < 0.60
            or not st.supporting_evidence
            and not st.contradicting_evidence
        ]

        if unresolved_ids:
            return LoopDecisionResult(
                decision=ResearchLoopDecision.REFINE_SEARCH,
                rationale=f"{len(unresolved_ids)} atomic propositions require additional evidence corroboration.",
                unresolved_atomic_claim_ids=unresolved_ids,
            )

        # 4. All propositions have sufficient evidence and no conflicts -> TERMINATE
        return LoopDecisionResult(
            decision=ResearchLoopDecision.TERMINATE,
            rationale="All atomic claims achieved evidence sufficiency threshold without unresolved conflicts.",
            unresolved_atomic_claim_ids=[],
        )
