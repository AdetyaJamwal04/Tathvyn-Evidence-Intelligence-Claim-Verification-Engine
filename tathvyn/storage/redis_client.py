"""Async Redis Connection and Cache Client."""

from __future__ import annotations

from typing import Any

from redis.asyncio import ConnectionPool, Redis

from tathvyn.common.config import get_settings

_redis_pool: ConnectionPool[Any] | None = None


def get_redis_pool() -> ConnectionPool[Any]:
    """Obtain or initialize the global Redis connection pool."""
    global _redis_pool
    if _redis_pool is None:
        settings = get_settings()
        _redis_pool = ConnectionPool.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=20,
            socket_connect_timeout=0.3,
            socket_timeout=0.5,
        )
    return _redis_pool


def get_redis_client() -> Redis[Any]:
    """Obtain an async Redis client from the shared connection pool."""
    return Redis(connection_pool=get_redis_pool())
