"""Provider contract for sports results and participant data."""

from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict


class EventResult(BaseModel):
    """Normalized final or live result from a sports-data provider."""

    model_config = ConfigDict(frozen=True)

    provider_event_id: str
    status: str
    home_score: int | None = None
    away_score: int | None = None
    observed_at: datetime | None = None


class SportsDataProvider(Protocol):
    """Boundary for a provider specialized in results and sports metadata."""

    async def list_sports(self) -> list[str]: ...

    async def list_leagues(self, sport: str | None = None) -> list[str]: ...

    async def get_event_result(self, provider_event_id: str) -> EventResult: ...
