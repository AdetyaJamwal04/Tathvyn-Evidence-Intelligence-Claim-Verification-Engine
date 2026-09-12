"""Tests for Budget Tracker."""

import pytest

from tathvyn.common.enums import BudgetUnit, ResearchDepth
from tathvyn.common.exceptions import BudgetExhaustedError
from tathvyn.orchestration.budget import BudgetLimits, BudgetTracker


def test_budget_limits_by_depth() -> None:
    """Verify default limits differ across depths."""
    b_fast = BudgetTracker(depth=ResearchDepth.FAST)
    b_deep = BudgetTracker(depth=ResearchDepth.DEEP)

    assert b_fast.limits.max_iterations == 0
    assert b_deep.limits.max_iterations == 3
    assert b_fast.can_execute_iteration() is False
    assert b_deep.can_execute_iteration() is True


def test_budget_exhaustion_on_queries() -> None:
    """Verify budget limits query consumption."""
    custom = BudgetLimits(
        max_queries=2, max_iterations=2, max_tokens=1000, max_latency_seconds=10.0
    )
    tracker = BudgetTracker(custom_limits=custom)

    assert tracker.can_consume_queries(2) is True
    tracker.record_query(2)
    assert tracker.can_consume_queries(1) is False
    assert tracker.can_execute_iteration() is False


def test_hard_limit_exception() -> None:
    """Verify enforce_limits raises BudgetExhaustedError when exceeded."""
    custom = BudgetLimits(
        max_queries=2, max_iterations=2, max_tokens=1000, max_latency_seconds=10.0
    )
    tracker = BudgetTracker(custom_limits=custom)
    tracker.record_query(5)

    with pytest.raises(BudgetExhaustedError) as exc_info:
        tracker.enforce_limits()
    assert exc_info.value.details["resource_type"] == BudgetUnit.SEARCH_QUERIES.value
