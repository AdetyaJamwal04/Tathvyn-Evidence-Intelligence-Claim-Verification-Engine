"""Tests for Typed Domain Exception Classes."""

from tathvyn.common.exceptions import (
    BudgetExhaustedError,
    ClaimDecompositionError,
    ProviderError,
    ProviderRateLimitError,
    SecurityViolationError,
    SSRFAttemptError,
    UnsupportedLanguageError,
    VeriFactException,
)


def test_base_exception() -> None:
    """Verify base VeriFactException properties."""
    exc = VeriFactException(
        "Something failed", error_code="TEST_ERR", status_code=500, details={"k": "v"}
    )
    assert exc.message == "Something failed"
    assert exc.error_code == "TEST_ERR"
    assert exc.status_code == 500
    assert exc.details["k"] == "v"


def test_unsupported_language_error() -> None:
    """Verify UnsupportedLanguageError 422 error code."""
    exc = UnsupportedLanguageError("es", 0.95)
    assert exc.status_code == 422
    assert exc.error_code == "UNSUPPORTED_LANGUAGE"
    assert exc.details["detected_language"] == "es"


def test_decomposition_error() -> None:
    """Verify ClaimDecompositionError."""
    exc = ClaimDecompositionError("Failed to parse", "Raw claim")
    assert exc.status_code == 400
    assert exc.error_code == "DECOMPOSITION_FAILED"


def test_provider_errors() -> None:
    """Verify ProviderError and ProviderRateLimitError."""
    exc = ProviderError("tavily", "500 Server Error")
    assert exc.status_code == 502
    assert exc.error_code == "PROVIDER_ERROR"

    rate_exc = ProviderRateLimitError("brave", retry_after_seconds=10)
    assert rate_exc.status_code == 429
    assert rate_exc.error_code == "PROVIDER_RATE_LIMIT"
    assert rate_exc.details["retry_after_seconds"] == 10


def test_security_and_ssrf_errors() -> None:
    """Verify SSRFAttemptError and SecurityViolationError."""
    ssrf = SSRFAttemptError("http://127.0.0.1", "127.0.0.1")
    assert ssrf.status_code == 403
    assert ssrf.error_code == "SSRF_ATTEMPT_BLOCKED"

    sec = SecurityViolationError("Max size cap exceeded")
    assert sec.status_code == 400
    assert sec.error_code == "SECURITY_VIOLATION"


def test_budget_exhausted_error() -> None:
    """Verify BudgetExhaustedError."""
    budget = BudgetExhaustedError("search_queries", limit=12.0, consumed=13.0)
    assert budget.status_code == 408
    assert budget.error_code == "BUDGET_EXHAUSTED"
