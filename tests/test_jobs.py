import asyncio

from app.jobs.runner import JobLock, RetryPolicy, run_job, run_with_retries


class FakeLock(JobLock):
    def __init__(self, acquired: bool = True) -> None:
        self.acquired = acquired
        self.released = False

    async def acquire(self, key: str, ttl_seconds: int) -> bool:
        return self.acquired

    async def release(self, key: str) -> None:
        self.released = True


def test_job_is_skipped_when_lock_is_owned_by_another_worker() -> None:
    lock = FakeLock(acquired=False)

    async def run() -> None:
        assert await run_job("test", lambda: asyncio.sleep(0, result=1), lock=lock) is None
        assert lock.released is False

    asyncio.run(run())


def test_job_releases_lock_after_success() -> None:
    lock = FakeLock()

    async def run() -> None:
        assert await run_job("test", lambda: asyncio.sleep(0, result=1), lock=lock) == 1
        assert lock.released is True

    asyncio.run(run())


def test_retries_transient_failures_with_zero_backoff() -> None:
    attempts = 0

    async def operation() -> int:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise TimeoutError
        return attempts

    async def run() -> None:
        result = await run_with_retries(
            operation,
            policy=RetryPolicy(max_attempts=3, base_delay_seconds=0, max_delay_seconds=0),
        )
        assert result == 3

    asyncio.run(run())
