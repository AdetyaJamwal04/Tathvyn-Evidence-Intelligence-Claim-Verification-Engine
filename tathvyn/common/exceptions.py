"""Typed Domain Exception Hierarchy for VeriFact.

Provides explicit, structured exception types for claim intelligence, retrieval,
security, and verdict generation failures.
"""

from typing import Any


class VeriFactException(Exception):
    """Base exception for all domain and operational errors in VeriFact."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}


# ==============================================================================
# Claim Intelligence Exceptions
# ==============================================================================


class UnsupportedLanguageError(VeriFactException):
    """Raised when an input claim is detected in an unsupported language."""

    def __init__(self, detected_language: str, confidence: float) -> None:
        super().__init__(
            message=f"VeriFact MVP supports English claims only. Detected: '{detected_language}' (confidence: {confidence:.2f}).",
            error_code="UNSUPPORTED_LANGUAGE",
            status_code=422,
            details={"detected_language": detected_language, "confidence": confidence},
        )


class ClaimDecompositionError(VeriFactException):
    """Raised when compound claim decomposition fails validation or produces hallucinations."""

    def __init__(self, message: str, raw_claim: str) -> None:
        super().__init__(
            message=message,
            error_code="DECOMPOSITION_FAILED",
            status_code=400,
            details={"raw_claim": raw_claim},
        )


# ==============================================================================
# Retrieval & Provider Exceptions
# ==============================================================================


class ProviderError(VeriFactException):
    """Base class for external search and LLM API failures."""

    def __init__(self, provider_name: str, message: str, status_code: int = 502) -> None:
        super().__init__(
            message=f"Provider '{provider_name}' failed: {message}",
            error_code="PROVIDER_ERROR",
            status_code=status_code,
            details={"provider": provider_name},
        )


class ProviderRateLimitError(ProviderError):
    """Raised when an external API returns HTTP 429 Too Many Requests."""

    def __init__(self, provider_name: str, retry_after_seconds: int = 5) -> None:
        super().__init__(
            provider_name=provider_name,
            message=f"Rate limit exceeded on provider '{provider_name}'.",
            status_code=429,
        )
        self.error_code = "PROVIDER_RATE_LIMIT"
        self.details["retry_after_seconds"] = retry_after_seconds


class DocumentFetchError(VeriFactException):
    """Raised when web document download or parsing fails."""

    def __init__(self, url: str, reason: str, status_code: int = 502) -> None:
        super().__init__(
            message=f"Failed to fetch document from '{url}': {reason}",
            error_code="DOCUMENT_FETCH_FAILED",
            status_code=status_code,
            details={"url": url, "reason": reason},
        )


# ==============================================================================
# Security & Safety Exceptions
# ==============================================================================


class SSRFAttemptError(VeriFactException):
    """Raised when a candidate URL resolves to a forbidden or private IP range."""

    def __init__(self, url: str, resolved_ip: str) -> None:
        super().__init__(
            message=f"SSRF violation: URL '{url}' resolved to blocked IP '{resolved_ip}'.",
            error_code="SSRF_ATTEMPT_BLOCKED",
            status_code=403,
            details={"url": url, "resolved_ip": resolved_ip},
        )


class SecurityViolationError(VeriFactException):
    """Raised when an input violates size caps or scheme constraints."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"Security constraint violated: {reason}",
            error_code="SECURITY_VIOLATION",
            status_code=400,
            details={"reason": reason},
        )


# ==============================================================================
# Orchestration & Budget Exceptions
# ==============================================================================


class BudgetExhaustedError(VeriFactException):
    """Raised when verification resource caps are reached."""

    def __init__(self, resource_type: str, limit: float, consumed: float) -> None:
        super().__init__(
            message=f"Budget exhausted for '{resource_type}': limit was {limit}, consumed {consumed}.",
            error_code="BUDGET_EXHAUSTED",
            status_code=408,
            details={"resource_type": resource_type, "limit": limit, "consumed": consumed},
        )
