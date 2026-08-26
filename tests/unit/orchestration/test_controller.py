"""Tests for Adaptive Research Loop Controller."""

from uuid import uuid4

from tathvyn.common.enums import (
    ConflictSeverity,
    ConflictType,
    ResearchDepth,
    ResearchLoopDecision,
)
from tathvyn.common.models.conflict import Conflict
from tathvyn.common.models.evidence import EvidenceState
from tathvyn.orchestration.budget import BudgetTracker
from tathvyn.orchestration.controller import AdaptiveLoopController


def test_controller_terminates_on_budget_exhaustion() -> None:
    """Verify controller terminates when budget cannot execute further iterations."""
    controller = AdaptiveLoopController()
    budget = BudgetTracker(depth=ResearchDepth.FAST)  # 0 max iterations

    res = controller.evaluate_loop_state(
        evidence_states=[],
        conflicts=[],
        budget_tracker=budget,
    )
    assert res.decision == ResearchLoopDecision.TERMINATE


def test_controller_resolves_conflict() -> None:
    """Verify controller triggers RESOLVE_CONFLICT on unresolved contradictions."""
    controller = AdaptiveLoopController()
    budget = BudgetTracker(depth=ResearchDepth.STANDARD)
    atomic_id = uuid4()

    conf = Conflict(
        conflict_id=uuid4(),
        atomic_claim_id=atomic_id,
        evidence_id_a=uuid4(),
        evidence_id_b=uuid4(),
        conflict_type=ConflictType.DIRECT_CONTRADICTION,
        severity=ConflictSeverity.CRITICAL,
    )

    res = controller.evaluate_loop_state(
        evidence_states=[],
        conflicts=[conf],
        budget_tracker=budget,
    )
    assert res.decision == ResearchLoopDecision.RESOLVE_CONFLICT
    assert atomic_id in res.unresolved_atomic_claim_ids


def test_controller_refines_search_on_low_coverage() -> None:
    """Verify controller triggers REFINE_SEARCH when evidence coverage is low."""
    controller = AdaptiveLoopController()
    budget = BudgetTracker(depth=ResearchDepth.STANDARD)
    atomic_id = uuid4()

    state = EvidenceState(
        atomic_claim_id=atomic_id,
        supporting_evidence=[],
        contradicting_evidence=[],
        coverage_score=0.20,
    )

    res = controller.evaluate_loop_state(
        evidence_states=[state],
        conflicts=[],
        budget_tracker=budget,
    )
    assert res.decision == ResearchLoopDecision.REFINE_SEARCH
    assert atomic_id in res.unresolved_atomic_claim_ids
