"""Sliding-Window Rate Limiting Subsystem and Middleware.

Enforces per-client IP request ceilings with RFC-7807 problem details
and standard HTTP rate-limiting headers.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from tathvyn.api.schemas import RFC7807ProblemDetails
from tathvyn.common.logging import get_logger

logger = get_logger("rate_limiter")


class RateLimiter:
    """In-memory sliding-window log rate limiter."""

    def __init__(self) -> None:
        # client_id -> deque of request timestamps
        self._clients: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(
        self,
        client_id: str,
        max_requests: int = 60,
        window_seconds: int = 60,
    ) -> tuple[bool, int, int]:
        """Check if request is permitted under sliding window.

        Args:
            client_id: Client identifier (IP address or API token).
            max_requests: Maximum allowable requests within window.
            window_seconds: Window duration in seconds.

        Returns:
            tuple[bool, int, int]: (is_allowed, remaining_requests, retry_after_seconds)
        """
        now = time.time()
        window_start = now - window_seconds
        timestamps = self._clients[client_id]

        # Purge timestamps outside the active sliding window
        while timestamps and timestamps[0] <= window_start:
            timestamps.popleft()

        if len(timestamps) >= max_requests:
            oldest = timestamps[0]
            retry_after = max(1, int(oldest + window_seconds - now))
            return False, 0, retry_after

        # Record current request timestamp
        timestamps.append(now)
        remaining = max(0, max_requests - len(timestamps))
        return True, remaining, 0

    def clear(self) -> None:
        """Clear all rate limit state."""
        self._clients.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI/Starlette middleware enforcing rate limits on verification endpoints."""

    def __init__(
        self,
        app: Any,
        rate_limiter: RateLimiter | None = None,
        max_requests: int = 60,
        window_seconds: int = 60,
    ) -> None:
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Only rate-limit API mutating and verification routes
        path = request.url.path
        if path.startswith("/api/v1/check") or path.startswith("/api/v1/research"):
            client_ip = (
                request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
                or (request.client.host if request.client else "127.0.0.1")
            )

            allowed, remaining, retry_after = self.rate_limiter.is_allowed(
                client_id=client_ip,
                max_requests=self.max_requests,
                window_seconds=self.window_seconds,
            )

            if not allowed:
                logger.warning(
                    "Rate limit exceeded",
                    client_ip=client_ip,
                    path=path,
                    retry_after=retry_after,
                )
                problem = RFC7807ProblemDetails(
                    type="https://Tathvyn.org/errors/rate-limit-exceeded",
                    title="Too Many Requests",
                    status=429,
                    detail=f"Rate limit exceeded. Please retry after {retry_after} seconds.",
                    instance=path,
                    error_code="RATE_LIMIT_EXCEEDED",
                )
                error_response = JSONResponse(
                    status_code=429,
                    content=problem.model_dump(exclude_none=True),
                )
                error_response.headers["Retry-After"] = str(retry_after)
                error_response.headers["X-RateLimit-Limit"] = str(self.max_requests)
                error_response.headers["X-RateLimit-Remaining"] = "0"
                return error_response

            response: Response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.max_requests)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            return response

        return await call_next(request)
