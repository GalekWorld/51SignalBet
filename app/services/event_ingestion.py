"""Idempotent ingestion of normalized provider events."""

from dataclasses import dataclass
from datetime import UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.text import normalize_name
from app.db.models import Event, League, Sport, Team
from app.domain.sports import EventStatus, validate_event_participants
from app.providers.contracts import OddsProvider, ProviderEvent


@dataclass(frozen=True)
class IngestionResult:
    """Counters and skipped records from one ingestion run."""

    created: int
    updated: int
    skipped: int


class EventIngestionService:
    """Synchronize provider event summaries into the internal sports model."""

    def __init__(self, session: AsyncSession, provider: OddsProvider) -> None:
        self._session = session
        self._provider = provider

    async def ingest_events(
        self,
        *,
        sport: str | None = None,
        league: str | None = None,
        start_from: int | None = None,
        start_to: int | None = None,
    ) -> IngestionResult:
        """Fetch all provider pages and upsert each complete event."""

        created = updated = skipped = 0
        cursor: str | None = None
        while True:
            events, cursor = await self._provider.list_events(
                sport=sport,
                league=league,
                start_from=start_from,
                start_to=start_to,
                cursor=cursor,
            )
            for provider_event in events:
                outcome = await self._upsert(provider_event)
                if outcome == "created":
                    created += 1
                elif outcome == "skipped":
                    skipped += 1
                else:
                    updated += 1
            if cursor is None:
                break
        await self._session.commit()
        return IngestionResult(created=created, updated=updated, skipped=skipped)

    async def _upsert(self, provider_event: ProviderEvent) -> str:
        """Insert or update one event; incomplete external records are ignored."""

        if not self._complete(provider_event):
            return "skipped"
        assert provider_event.sport is not None
        assert provider_event.home_team is not None
        assert provider_event.away_team is not None
        assert provider_event.start_time is not None

        sport_entity = await self._get_or_create_sport(provider_event.sport)
        league_entity = await self._get_or_create_league(sport_entity, provider_event.league)
        home = await self._get_or_create_team(sport_entity, league_entity, provider_event.home_team)
        away = await self._get_or_create_team(sport_entity, league_entity, provider_event.away_team)
        validate_event_participants(home.id, away.id)

        existing = await self._session.scalar(
            select(Event).where(
                Event.provider == "odds_api",
                Event.provider_event_id == provider_event.provider_event_id,
            )
        )
        start_time = provider_event.start_time.astimezone(UTC)
        if existing is None:
            self._session.add(
                Event(
                    provider="odds_api",
                    provider_event_id=provider_event.provider_event_id,
                    sport_id=sport_entity.id,
                    league_id=league_entity.id if league_entity else None,
                    home_team_id=home.id,
                    away_team_id=away.id,
                    start_time=start_time,
                    status=EventStatus.SCHEDULED,
                )
            )
            await self._session.flush()
            return "created"
        existing.sport_id = sport_entity.id
        existing.league_id = league_entity.id if league_entity else None
        existing.home_team_id = home.id
        existing.away_team_id = away.id
        existing.start_time = start_time
        await self._session.flush()
        return "updated"

    @staticmethod
    def _complete(provider_event: ProviderEvent) -> bool:
        return all(
            (
                provider_event.sport,
                provider_event.home_team,
                provider_event.away_team,
                provider_event.start_time,
            )
        )

    async def _get_or_create_sport(self, value: str) -> Sport:
        code = normalize_name(value).replace(" ", "_")
        entity = await self._session.scalar(select(Sport).where(Sport.code == code))
        if entity is None:
            entity = Sport(code=code, name=value.strip())
            self._session.add(entity)
            await self._session.flush()
        return entity

    async def _get_or_create_league(self, sport: Sport, value: str | None) -> League | None:
        if not value:
            return None
        code = normalize_name(value).replace(" ", "_")
        entity = await self._session.scalar(
            select(League).where(League.sport_id == sport.id, League.code == code)
        )
        if entity is None:
            entity = League(sport_id=sport.id, code=code, name=value.strip())
            self._session.add(entity)
            await self._session.flush()
        return entity

    async def _get_or_create_team(self, sport: Sport, league: League | None, value: str) -> Team:
        normalized = normalize_name(value)
        entity = await self._session.scalar(
            select(Team).where(Team.sport_id == sport.id, Team.normalized_name == normalized)
        )
        if entity is None:
            entity = Team(
                sport_id=sport.id,
                league_id=league.id if league else None,
                name=value.strip(),
                normalized_name=normalized,
            )
            self._session.add(entity)
            await self._session.flush()
        elif entity.league_id is None and league is not None:
            entity.league_id = league.id
        return entity
