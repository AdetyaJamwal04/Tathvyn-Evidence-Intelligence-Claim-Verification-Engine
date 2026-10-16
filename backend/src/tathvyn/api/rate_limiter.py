"""Sliding-Window Rate Limiting Subsystem and Middleware.

Enforces per-client IP request ceilings with RFC-7807 problem details,
standard HTTP rate-limiting headers, trusted proxy validation, and LRU pruning.
"""

from __future__ import annotations

import time
from collections import OrderedDict, deque
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from tathvyn.api.schemas import RFC7807ProblemDetails
from tathvyn.common.logging import get_logger

logger = get_logger("rate_limiter")

DEFAULT_MAX_CLIENTS = 10000
DEFAULT_TRUSTED_PROXIES = {"127.0.0.1", "::1", "localhost"}


class RateLimiter:
    """In-memory sliding-window log rate limiter with bounded LRU eviction."""

    def __init__(self, max_clients: int = DEFAULT_MAX_CLIENTS) -> None:
        # client_id -> deque of request timestamps
        self._clients: OrderedDict[str, deque[float]] = OrderedDict()
        self.max_clients = max_clients

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

        timestamps = self._clients.get(client_id)
        if timestamps is None:
            # Enforce max client capacity to prevent unbounded memory growth
            if len(self._clients) >= self.max_clients:
                self._clients.popitem(last=False)
            timestamps = deque()
            self._clients[client_id] = timestamps

        # Purge timestamps outside the active sliding window
        while timestamps and timestamps[0] <= window_start:
            timestamps.popleft()

        # Move client to end for LRU recency
        self._clients.move_to_end(client_id)

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
        trusted_proxies: set[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.trusted_proxies = trusted_proxies or DEFAULT_TRUSTED_PROXIES

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Only rate-limit API mutating and verification routes
        path = request.url.path
        if path.startswith("/api/v1/check") or path.startswith("/api/v1/research") or path.startswith("/api/v1/verify"):
            direct_ip = request.client.host if request.client else "127.0.0.1"

            # Only trust X-Forwarded-For if client directly connects from a trusted proxy
            if direct_ip in self.trusted_proxies and "X-Forwarded-For" in request.headers:
                forwarded_for = request.headers.get("X-Forwarded-For", "").split(",")
                client_ip = forwarded_for[0].strip() if forwarded_for else direct_ip
            else:
                client_ip = direct_ip

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
