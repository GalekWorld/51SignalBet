"""Favorite management use case."""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Favorite
from app.domain.favorites import FavoriteType


class FavoriteService:
    """Add, remove and list favorites idempotently."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user_id: UUID, favorite_type: FavoriteType, target_id: UUID) -> Favorite:
        favorite = await self._session.scalar(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.favorite_type == favorite_type,
                Favorite.target_id == target_id,
            )
        )
        if favorite is None:
            favorite = Favorite(user_id=user_id, favorite_type=favorite_type, target_id=target_id)
            self._session.add(favorite)
            await self._session.flush()
        await self._session.commit()
        return favorite

    async def remove(self, user_id: UUID, favorite_type: FavoriteType, target_id: UUID) -> bool:
        result = await self._session.execute(
            delete(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.favorite_type == favorite_type,
                Favorite.target_id == target_id,
            )
        )
        await self._session.commit()
        return bool(getattr(result, "rowcount", 0))

    async def list(
        self, user_id: UUID, favorite_type: FavoriteType | None = None
    ) -> list[Favorite]:
        statement = (
            select(Favorite).where(Favorite.user_id == user_id).order_by(Favorite.created_at)
        )
        if favorite_type is not None:
            statement = statement.where(Favorite.favorite_type == favorite_type)
        return list(await self._session.scalars(statement))
