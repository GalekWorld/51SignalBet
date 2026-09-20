"""Redis-backed distributed job lock."""

from uuid import uuid4

from redis.asyncio import Redis

from app.jobs.runner import JobLock


class RedisJobLock(JobLock):
    """Best-effort Redis lock with token-checked release."""

    _release_script = """
    if redis.call('get', KEYS[1]) == ARGV[1] then
        return redis.call('del', KEYS[1])
    end
    return 0
    """

    def __init__(self, redis: Redis, *, prefix: str = "betting:job:") -> None:
        self._redis = redis
        self._prefix = prefix
        self._tokens: dict[str, str] = {}

    async def acquire(self, key: str, ttl_seconds: int) -> bool:
        token = str(uuid4())
        acquired = await self._redis.set(f"{self._prefix}{key}", token, nx=True, ex=ttl_seconds)
        if acquired:
            self._tokens[key] = token
        return bool(acquired)

    async def release(self, key: str) -> None:
        token = self._tokens.pop(key, None)
        if token is not None:
            await self._redis.eval(  # type: ignore[misc]
                self._release_script, 1, f"{self._prefix}{key}", token
            )
