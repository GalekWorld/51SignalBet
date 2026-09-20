"""Deterministic sports-data provider for tests and local development."""

from app.providers.errors import ProviderNotFound
from app.providers.sports_data import EventResult, SportsDataProvider


class FixtureSportsDataProvider(SportsDataProvider):
    """Fixture implementation kept separate from the odds provider contract."""

    def __init__(
        self,
        *,
        sports: list[str] | None = None,
        leagues: dict[str, list[str]] | None = None,
        results: dict[str, EventResult] | None = None,
    ) -> None:
        self._sports = sports or []
        self._leagues = leagues or {}
        self._results = results or {}

    async def list_sports(self) -> list[str]:
        return list(self._sports)

    async def list_leagues(self, sport: str | None = None) -> list[str]:
        if sport is None:
            return [league for values in self._leagues.values() for league in values]
        return list(self._leagues.get(sport, []))

    async def get_event_result(self, provider_event_id: str) -> EventResult:
        try:
            return self._results[provider_event_id]
        except KeyError as exc:
            raise ProviderNotFound(f"sports result {provider_event_id} was not found") from exc
