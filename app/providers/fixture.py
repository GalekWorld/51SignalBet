"""Deterministic second provider implementation for development and contract tests."""

from collections.abc import Iterable

from app.providers.contracts import (
    OddsProvider,
    ProviderEvent,
    ProviderOddsSnapshot,
)
from app.providers.errors import ProviderNotFound


class FixtureOddsProvider(OddsProvider):
    """Provider backed by injected normalized fixtures, never by production data."""

    def __init__(
        self,
        *,
        sports: Iterable[str] = (),
        leagues: dict[str, list[str]] | None = None,
        events: Iterable[ProviderEvent] = (),
        odds: dict[str, ProviderOddsSnapshot] | None = None,
    ) -> None:
        self._sports = list(sports)
        self._leagues = leagues or {}
        self._events = list(events)
        self._odds = odds or {}

    async def list_sports(self) -> list[str]:
        return list(self._sports)

    async def list_leagues(self, sport: str | None = None) -> list[str]:
        if sport is None:
            return [league for leagues in self._leagues.values() for league in leagues]
        return list(self._leagues.get(sport, []))

    async def list_events(
        self,
        *,
        sport: str | None = None,
        league: str | None = None,
        start_from: int | None = None,
        start_to: int | None = None,
        cursor: str | None = None,
        limit: int = 200,
    ) -> tuple[list[ProviderEvent], str | None]:
        if cursor not in {None, "0"}:
            return [], None
        filtered = [
            event
            for event in self._events
            if (sport is None or event.sport == sport)
            and (league is None or event.league == league)
        ]
        return filtered[:limit], None

    async def get_event(self, provider_event_id: str) -> ProviderEvent:
        for event in self._events:
            if event.provider_event_id == provider_event_id:
                return event
        raise ProviderNotFound(f"fixture event {provider_event_id} was not found")

    async def get_odds(
        self,
        provider_event_id: str,
        *,
        bookmakers: list[str] | None = None,
        market_keys: list[str] | None = None,
        limit: int = 2000,
        cursor: str | None = None,
    ) -> ProviderOddsSnapshot:
        del bookmakers, market_keys, limit, cursor
        try:
            return self._odds[provider_event_id]
        except KeyError as exc:
            raise ProviderNotFound(f"fixture odds {provider_event_id} were not found") from exc
