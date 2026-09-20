"""Small async job runner with bounded retries and optional locking."""

import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

from app.providers.errors import ProviderRateLimited, ProviderUnavailable

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    """Retry limits for transient job failures."""

    max_attempts: int = 3
    base_delay_seconds: float = 0.5
    max_delay_seconds: float = 8.0


class JobLock:
    """Minimal async lock contract for distributed coordination."""

    async def acquire(self, key: str, ttl_seconds: int) -> bool:
        raise NotImplementedError

    async def release(self, key: str) -> None:
        raise NotImplementedError


async def run_with_retries(  # noqa: UP047
    operation: Callable[[], Awaitable[T]],
    *,
    policy: RetryPolicy | None = None,
    retryable: tuple[type[Exception], ...] = (
        OSError,
        TimeoutError,
        ProviderRateLimited,
        ProviderUnavailable,
    ),
) -> T:  # noqa: UP047
    """Run an operation with bounded exponential backoff and jitter."""

    policy = policy or RetryPolicy()
    if policy.max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    for attempt in range(policy.max_attempts):
        try:
            return await operation()
        except retryable:
            if attempt == policy.max_attempts - 1:
                raise
            delay = min(policy.max_delay_seconds, policy.base_delay_seconds * (2**attempt))
            await asyncio.sleep(delay + random.uniform(0, min(0.25, delay / 2)))
    raise AssertionError("unreachable")


async def run_job(  # noqa: UP047
    name: str,
    operation: Callable[[], Awaitable[T]],
    *,
    lock: JobLock | None = None,
    lock_ttl_seconds: int = 300,
    policy: RetryPolicy | None = None,
) -> T | None:  # noqa: UP047
    """Execute one idempotent job, skipping it when another worker owns its lock."""

    if lock is not None and not await lock.acquire(name, lock_ttl_seconds):
        return None
    try:
        return await run_with_retries(operation, policy=policy)
    finally:
        if lock is not None:
            await lock.release(name)
