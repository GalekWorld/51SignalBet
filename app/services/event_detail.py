"""Event detail use case."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Event
from app.services.today_events import timezone_or_utc


class EventNotFound(LookupError):
    """Requested internal event does not exist."""


@dataclass(frozen=True)
class EventDetail:
    """Presentation-neutral event detail."""

    id: UUID
    start_time: datetime
    home_team: str
    away_team: str
    league: str | None
    sport: str
    status: str
    home_score: int | None
    away_score: int | None
    venue: str | None


class EventDetailService:
    """Load a complete event without exposing ORM objects to interfaces."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, event_id: UUID, *, timezone_name: str = "UTC") -> EventDetail:
        event = await self._session.scalar(
            select(Event)
            .options(
                selectinload(Event.sport),
                selectinload(Event.league),
                selectinload(Event.home_team),
                selectinload(Event.away_team),
            )
            .where(Event.id == event_id)
        )
        if event is None:
            raise EventNotFound(f"event {event_id} was not found")
        local_start = event.start_time.astimezone(timezone_or_utc(timezone_name))
        return EventDetail(
            id=event.id,
            start_time=local_start,
            home_team=event.home_team.name,
            away_team=event.away_team.name,
            league=event.league.name if event.league else None,
            sport=event.sport.name,
            status=str(event.status),
            home_score=event.home_score,
            away_score=event.away_score,
            venue=event.venue,
        )
