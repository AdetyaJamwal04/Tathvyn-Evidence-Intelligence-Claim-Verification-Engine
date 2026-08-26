"""Unit Tests for Degradation Controller and Load Shedding."""

from tathvyn.common.enums import VerificationMode
from tathvyn.orchestration.degradation import DegradationController


def test_degradation_normal_load() -> None:
    controller = DegradationController(max_backlog_threshold=10, max_latency_threshold_seconds=15.0)

    for _ in range(5):
        controller.record_request(latency_seconds=2.0, success=True)

    # Normal conditions should preserve requested depth
    assert controller.adjust_depth(VerificationMode.DEEP, current_queue_backlog=2) == VerificationMode.DEEP
    assert controller.adjust_depth(VerificationMode.STANDARD, current_queue_backlog=2) == VerificationMode.STANDARD
    assert not controller.is_circuit_open()


def test_degradation_heavy_backlog() -> None:
    controller = DegradationController(max_backlog_threshold=10, max_latency_threshold_seconds=15.0)

    # Heavy backlog: depth should degrade
    assert controller.adjust_depth(VerificationMode.DEEP, current_queue_backlog=15) == VerificationMode.STANDARD
    assert controller.adjust_depth(VerificationMode.STANDARD, current_queue_backlog=15) == VerificationMode.FAST
    assert controller.adjust_depth(VerificationMode.FAST, current_queue_backlog=15) == VerificationMode.FAST


def test_degradation_high_latency() -> None:
    controller = DegradationController(max_backlog_threshold=10, max_latency_threshold_seconds=5.0)

    for _ in range(5):
        controller.record_request(latency_seconds=8.0, success=True)

    # High average latency should degrade depth
    assert controller.get_average_latency() == 8.0
    assert controller.adjust_depth(VerificationMode.DEEP, current_queue_backlog=1) == VerificationMode.STANDARD


def test_circuit_breaker_trip_on_high_error_rate() -> None:
    controller = DegradationController(error_rate_threshold=0.40, window_size=20)

    # Record 6 failures out of 10 requests (60% failure rate)
    for _ in range(4):
        controller.record_request(latency_seconds=1.0, success=True)
    for _ in range(6):
        controller.record_request(latency_seconds=1.0, success=False)

    assert controller.is_circuit_open()
