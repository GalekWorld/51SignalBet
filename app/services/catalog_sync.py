"""Synchronization of provider sports and league catalogs."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.text import normalize_name
from app.db.models import League, Sport
from app.providers.contracts import OddsProvider


class CatalogSyncService:
    """Upsert provider catalog names into internal identities."""

    def __init__(self, session: AsyncSession, provider: OddsProvider) -> None:
        self._session = session
        self._provider = provider

    async def sync_sports(self) -> int:
        created = 0
        for name in await self._provider.list_sports():
            code = normalize_name(name).replace(" ", "_")
            if await self._session.scalar(select(Sport).where(Sport.code == code)) is None:
                self._session.add(Sport(code=code, name=name.strip()))
                created += 1
        await self._session.commit()
        return created

    async def sync_leagues(self, sport: str) -> int:
        sport_code = normalize_name(sport).replace(" ", "_")
        sport_entity = await self._session.scalar(select(Sport).where(Sport.code == sport_code))
        if sport_entity is None:
            return 0
        created = 0
        for name in await self._provider.list_leagues(sport=sport):
            code = normalize_name(name).replace(" ", "_")
            exists = await self._session.scalar(
                select(League).where(League.sport_id == sport_entity.id, League.code == code)
            )
            if exists is None:
                self._session.add(League(sport_id=sport_entity.id, code=code, name=name.strip()))
                created += 1
        await self._session.commit()
        return created
