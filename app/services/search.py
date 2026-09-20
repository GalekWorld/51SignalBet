"""Database-backed event search with accent/case normalization."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from app.core.text import normalize_name
from app.db.models import Event, League, Team


@dataclass(frozen=True)
class EventSearchResult:
    """Compact search result suitable for Telegram or API responses."""

    event_id: UUID
    start_time: datetime
    home_team: str
    away_team: str
    league: str | None


@dataclass(frozen=True)
class SearchPage:
    """Bounded search response with offset continuation."""

    items: list[EventSearchResult]
    next_offset: int | None


class EventSearchService:
    """Search event participants and leagues without an external search engine."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(self, query: str, *, offset: int = 0, limit: int = 20) -> SearchPage:
        normalized = normalize_name(query)
        if not normalized:
            return SearchPage(items=[], next_offset=None)
        if offset < 0 or not 1 <= limit <= 100:
            raise ValueError("offset must be non-negative and limit must be between 1 and 100")
        pattern = f"%{normalized}%"
        home_team = aliased(Team)
        away_team = aliased(Team)
        result = await self._session.scalars(
            select(Event)
            .join(home_team, Event.home_team_id == home_team.id)
            .join(away_team, Event.away_team_id == away_team.id)
            .outerjoin(League, Event.league_id == League.id)
            .options(
                selectinload(Event.home_team),
                selectinload(Event.away_team),
                selectinload(Event.league),
            )
            .where(
                or_(
                    home_team.normalized_name.ilike(pattern),
                    away_team.normalized_name.ilike(pattern),
                    League.code.ilike(pattern),
                    League.name.ilike(pattern),
                )
            )
            .order_by(Event.start_time)
            .offset(offset)
            .limit(limit + 1)
        )
        events = list(result)
        has_more = len(events) > limit
        items = [
            EventSearchResult(
                event_id=event.id,
                start_time=event.start_time,
                home_team=event.home_team.name,
                away_team=event.away_team.name,
                league=event.league.name if event.league else None,
            )
            for event in events[:limit]
        ]
        return SearchPage(items=items, next_offset=offset + limit if has_more else None)
