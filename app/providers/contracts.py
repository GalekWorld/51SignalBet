"""Provider-independent contracts and normalized return models."""

from datetime import datetime
from decimal import Decimal
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class ProviderEvent(BaseModel):
    """Normalized event returned by a sports-data provider."""

    model_config = ConfigDict(frozen=True)

    provider_event_id: str = Field(min_length=1)
    sport: str | None = None
    league: str | None = None
    start_time: datetime | None = None
    home_team: str | None = None
    away_team: str | None = None


class ProviderOddsLine(BaseModel):
    """Normalized odds line; provider-specific field names do not leak out."""

    model_config = ConfigDict(frozen=True)

    id: str
    provider_event_id: str
    bookmaker: str
    market_key: str
    selection: str | None = None
    line: Decimal | None = None
    odds: Decimal | None = None
    is_available: bool = True


class ProviderOddsSnapshot(BaseModel):
    """Normalized point-in-time odds response."""

    model_config = ConfigDict(frozen=True)

    provider_event_id: str
    as_of: datetime | None = None
    lines: tuple[ProviderOddsLine, ...]
    next_cursor: str | None = None
    resume: str


class OddsProvider(Protocol):
    """Contract consumed by application services, independent of HTTP details."""

    async def list_sports(self) -> list[str]: ...

    async def list_leagues(self, sport: str | None = None) -> list[str]: ...

    async def list_events(
        self,
        *,
        sport: str | None = None,
        league: str | None = None,
        start_from: int | None = None,
        start_to: int | None = None,
        cursor: str | None = None,
        limit: int = 200,
    ) -> tuple[list[ProviderEvent], str | None]: ...

    async def get_event(self, provider_event_id: str) -> ProviderEvent: ...

    async def get_odds(
        self,
        provider_event_id: str,
        *,
        bookmakers: list[str] | None = None,
        market_keys: list[str] | None = None,
        limit: int = 2000,
        cursor: str | None = None,
    ) -> ProviderOddsSnapshot: ...
