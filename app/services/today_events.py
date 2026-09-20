"""Use case for listing today's events in a user's timezone."""

from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Event


@dataclass(frozen=True)
class TodayEvent:
    """Small presentation-neutral event summary."""

    id: str
    start_time: datetime
    home_team: str
    away_team: str
    league: str | None
    status: str


def timezone_or_utc(timezone_name: str) -> ZoneInfo:
    """Return a valid timezone, falling back safely for stale user settings."""

    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def today_window_utc(
    timezone_name: str,
    *,
    now: datetime | None = None,
) -> tuple[datetime, datetime]:
    """Return the user's local calendar day as a half-open UTC interval."""

    zone = timezone_or_utc(timezone_name)
    current = (now or datetime.now(UTC)).astimezone(zone)
    start_local = datetime.combine(current.date(), time.min, tzinfo=zone)
    end_local = start_local + timedelta(days=1)
    return start_local.astimezone(UTC), end_local.astimezone(UTC)


class TodayEventsService:
    """Query today's events with bounded results and eager-loaded names."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_today(
        self,
        *,
        timezone_name: str,
        now: datetime | None = None,
        limit: int = 20,
    ) -> list[TodayEvent]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        start, end = today_window_utc(timezone_name, now=now)
        result = await self._session.scalars(
            select(Event)
            .options(
                selectinload(Event.home_team),
                selectinload(Event.away_team),
                selectinload(Event.league),
            )
            .where(Event.start_time >= start, Event.start_time < end)
            .order_by(Event.start_time)
            .limit(limit)
        )
        return [
            TodayEvent(
                id=str(event.id),
                start_time=event.start_time,
                home_team=event.home_team.name,
                away_team=event.away_team.name,
                league=event.league.name if event.league else None,
                status=str(event.status),
            )
            for event in result
        ]
