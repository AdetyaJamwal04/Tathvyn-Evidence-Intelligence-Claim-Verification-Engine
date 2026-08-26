"""Dynamic Load Degradation and Circuit Breaking Controller.

Monitors system load, queue backlog, and provider error rates to gracefully
shed load and adjust verification depth under peak traffic conditions.
"""

from __future__ import annotations

import time
from collections import deque

from tathvyn.common.enums import VerificationMode
from tathvyn.common.logging import get_logger

logger = get_logger("degradation_controller")


class DegradationController:
    """Dynamically scales research depth and protects against cascading downstream failure."""

    def __init__(
        self,
        max_backlog_threshold: int = 15,
        max_latency_threshold_seconds: float = 18.0,
        error_rate_threshold: float = 0.50,
        window_size: int = 50,
    ) -> None:
        self.max_backlog_threshold = max_backlog_threshold
        self.max_latency_threshold_seconds = max_latency_threshold_seconds
        self.error_rate_threshold = error_rate_threshold

        self._latencies: deque[float] = deque(maxlen=window_size)
        self._request_outcomes: deque[bool] = deque(maxlen=window_size)  # True = success, False = fail
        self._circuit_open_until: float = 0.0

    def record_request(self, latency_seconds: float, success: bool = True) -> None:
        """Record the outcome and latency of a verification request."""
        self._latencies.append(latency_seconds)
        self._request_outcomes.append(success)

        # Check if error rate exceeds threshold
        if len(self._request_outcomes) >= 10:
            failures = sum(1 for outcome in self._request_outcomes if not outcome)
            rate = failures / len(self._request_outcomes)
            if rate >= self.error_rate_threshold:
                # Trip circuit breaker for 30 seconds
                self._circuit_open_until = time.time() + 30.0
                logger.warning(
                    "High error rate detected, tripping circuit breaker",
                    error_rate=round(rate, 2),
                    duration_seconds=30,
                )

    def is_circuit_open(self) -> bool:
        """Return True if circuit breaker is actively open/tripped."""
        return time.time() < self._circuit_open_until

    def get_average_latency(self) -> float:
        """Return rolling average request latency."""
        if not self._latencies:
            return 0.0
        return sum(self._latencies) / len(self._latencies)

    def adjust_depth(
        self,
        requested_depth: VerificationMode,
        current_queue_backlog: int = 0,
    ) -> VerificationMode:
        """Dynamically degrade verification depth if system is under heavy load.

        Args:
            requested_depth: The user-requested VerificationMode.
            current_queue_backlog: Number of pending jobs in worker queue.

        Returns:
            VerificationMode: Adjusted depth mode (degraded if necessary).
        """
        avg_latency = self.get_average_latency()

        # Severe load: queue backlog > threshold OR latency > threshold
        if current_queue_backlog > self.max_backlog_threshold or avg_latency > self.max_latency_threshold_seconds:
            if requested_depth == VerificationMode.DEEP:
                logger.warning(
                    "Degrading verification depth from DEEP to STANDARD under heavy load",
                    backlog=current_queue_backlog,
                    avg_latency=round(avg_latency, 2),
                )
                return VerificationMode.STANDARD
            elif requested_depth == VerificationMode.STANDARD:
                logger.warning(
                    "Degrading verification depth from STANDARD to FAST under heavy load",
                    backlog=current_queue_backlog,
                    avg_latency=round(avg_latency, 2),
                )
                return VerificationMode.FAST

        return requested_depth


_DEFAULT_DEGRADATION_CONTROLLER: DegradationController | None = None


def get_degradation_controller() -> DegradationController:
    """Return shared singleton DegradationController."""
    global _DEFAULT_DEGRADATION_CONTROLLER
    if _DEFAULT_DEGRADATION_CONTROLLER is None:
        _DEFAULT_DEGRADATION_CONTROLLER = DegradationController()
    return _DEFAULT_DEGRADATION_CONTROLLER
