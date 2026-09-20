"""FastAPI application entry point and dependency health endpoints."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import dispose_engine, get_engine


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Own shared database and Redis clients for the API process."""

    redis = Redis.from_url(get_settings().redis_url, decode_responses=True)
    application.state.redis = redis
    try:
        yield
    finally:
        await redis.aclose()
        await dispose_engine()


def create_app() -> FastAPI:
    """Build the API without connecting to infrastructure at import time."""

    settings = get_settings()
    application = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

    @application.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        """Backward-compatible liveness endpoint."""

        return {"status": "ok", "environment": settings.app_env}

    @application.get("/health/live", tags=["system"])
    async def liveness() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/health/ready", tags=["system"])
    async def readiness() -> JSONResponse:
        checks: dict[str, str] = {}
        try:
            async with get_engine().connect() as connection:
                await connection.execute(text("SELECT 1"))
            checks["postgres"] = "ok"
        except Exception:
            checks["postgres"] = "unavailable"
        try:
            await application.state.redis.ping()
            checks["redis"] = "ok"
        except Exception:
            checks["redis"] = "unavailable"
        ready = all(value == "ok" for value in checks.values())
        return JSONResponse(
            {"status": "ok" if ready else "unready", "checks": checks},
            status_code=200 if ready else 503,
        )

    @application.get("/health/provider", tags=["system"])
    async def provider_health() -> dict[str, str]:
        return {"status": "not_checked", "provider": "odds_api"}

    return application


app = create_app()
