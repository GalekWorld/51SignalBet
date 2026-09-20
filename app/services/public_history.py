"""Publication and retrieval of immutable system picks."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PublishedPick


class PublicHistoryService:
    """Persist complete publication snapshots and never recalculate them later."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def publish(
        self,
        *,
        event_id: UUID,
        bookmaker_id: UUID,
        market: str,
        selection: str,
        odds: Decimal,
        fair_probability: Decimal,
        model_probability: Decimal | None,
        source: str,
        publication_key: str,
        strategy_version: str | None = None,
        published_at: datetime | None = None,
    ) -> PublishedPick:
        existing = await self._session.scalar(
            select(PublishedPick).where(PublishedPick.publication_key == publication_key)
        )
        if existing is not None:
            return existing
        pick = PublishedPick(
            event_id=event_id,
            bookmaker_id=bookmaker_id,
            market=market,
            selection=selection,
            odds=odds,
            fair_probability=fair_probability,
            model_probability=model_probability,
            published_at=(published_at or datetime.now(UTC)).astimezone(UTC),
            strategy_version=strategy_version,
            source=source,
            publication_key=publication_key,
        )
        self._session.add(pick)
        await self._session.commit()
        return pick

    async def recent(self, *, limit: int = 20, offset: int = 0) -> list[PublishedPick]:
        if offset < 0 or not 1 <= limit <= 100:
            raise ValueError("offset must be non-negative and limit must be between 1 and 100")
        return list(
            await self._session.scalars(
                select(PublishedPick)
                .order_by(PublishedPick.published_at.desc())
                .offset(offset)
                .limit(limit)
            )
        )
