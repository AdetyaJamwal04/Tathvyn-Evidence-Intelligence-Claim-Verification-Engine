"""Token, Search Query, and Latency Budget Manager.

Enforces execution constraints across verification depths (FAST, STANDARD, DEEP)
to prevent unbounded API expenditure and latency overruns.
"""

import time
from typing import NamedTuple

from tathvyn.common.enums import BudgetUnit, ResearchDepth
from tathvyn.common.exceptions import BudgetExhaustedError
from tathvyn.common.logging import get_logger

logger = get_logger("budget_tracker")


class BudgetLimits(NamedTuple):
    """Configuration limits for an execution run."""

    max_queries: int
    max_iterations: int
    max_tokens: int
    max_latency_seconds: float


# Depth-specific budget specifications
_DEFAULT_LIMITS: dict[ResearchDepth, BudgetLimits] = {
    ResearchDepth.FAST: BudgetLimits(
        max_queries=3,
        max_iterations=0,
        max_tokens=10_000,
        max_latency_seconds=6.0,
    ),
    ResearchDepth.STANDARD: BudgetLimits(
        max_queries=8,
        max_iterations=2,
        max_tokens=35_000,
        max_latency_seconds=18.0,
    ),
    ResearchDepth.DEEP: BudgetLimits(
        max_queries=15,
        max_iterations=3,
        max_tokens=80_000,
        max_latency_seconds=40.0,
    ),
}


class BudgetTracker:
    """Tracks and enforces resource consumption for a research verification execution."""

    def __init__(
        self,
        depth: ResearchDepth = ResearchDepth.STANDARD,
        custom_limits: BudgetLimits | None = None,
    ) -> None:
        self.depth = depth
        self.limits = custom_limits or _DEFAULT_LIMITS.get(
            depth, _DEFAULT_LIMITS[ResearchDepth.STANDARD]
        )
        self.queries_consumed = 0
        self.tokens_consumed = 0
        self.iterations_completed = 0
        self.start_time = time.perf_counter()

    @property
    def elapsed_seconds(self) -> float:
        """Wall-clock elapsed execution seconds."""
        return time.perf_counter() - self.start_time

    def can_execute_iteration(self) -> bool:
        """Check if an additional iterative research cycle is permitted."""
        if self.iterations_completed >= self.limits.max_iterations:
            return False
        if self.elapsed_seconds >= self.limits.max_latency_seconds:
            return False
        return self.queries_consumed < self.limits.max_queries

    def can_consume_queries(self, count: int = 1) -> bool:
        """Check if search query budget allows count additional queries."""
        return (self.queries_consumed + count) <= self.limits.max_queries

    def record_query(self, count: int = 1) -> None:
        """Record executed search queries."""
        self.queries_consumed += count
        if self.queries_consumed > self.limits.max_queries:
            logger.warning(
                "Search query budget limit reached",
                current=self.queries_consumed,
                max=self.limits.max_queries,
            )

    def record_tokens(self, count: int) -> None:
        """Record consumed LLM/transformer tokens."""
        self.tokens_consumed += count

    def record_iteration(self) -> None:
        """Increment completed research iteration count."""
        self.iterations_completed += 1

    def enforce_limits(self) -> None:
        """Raise BudgetExhaustedError if hard resource limits are exceeded."""
        if self.elapsed_seconds > (self.limits.max_latency_seconds * 1.5):
            raise BudgetExhaustedError(
                resource_type=BudgetUnit.SECONDS.value,
                limit=self.limits.max_latency_seconds,
                consumed=self.elapsed_seconds,
            )
        if self.queries_consumed > (self.limits.max_queries * 1.5):
            raise BudgetExhaustedError(
                resource_type=BudgetUnit.SEARCH_QUERIES.value,
                limit=float(self.limits.max_queries),
                consumed=float(self.queries_consumed),
            )
