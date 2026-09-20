"""Async SQLAlchemy engine and session factory."""

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    return create_async_engine(
        get_settings().database_url, pool_pre_ping=True, pool_size=5, max_overflow=5
    )


@lru_cache
def create_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create a session factory lazily from runtime configuration."""

    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def dispose_engine() -> None:
    """Close the process-wide engine during application shutdown."""

    await get_engine().dispose()


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield a database session for application integrations."""

    factory = create_session_factory()
    async with factory() as session:
        yield session
