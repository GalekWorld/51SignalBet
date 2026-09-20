"""Adapter for the documented Odds API HTTP contract."""

import asyncio
import random
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from email.utils import parsedate_to_datetime
from typing import Any

import httpx

from app.providers.contracts import (
    OddsProvider,
    ProviderEvent,
    ProviderOddsLine,
    ProviderOddsSnapshot,
)
from app.providers.errors import (
    ProviderAuthenticationError,
    ProviderError,
    ProviderNotFound,
    ProviderRateLimited,
    ProviderUnavailable,
)


class OddsApiProvider(OddsProvider):
    """Async adapter for ``https://api.odds-api.net/v1``."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.odds-api.net/v1",
        client: httpx.AsyncClient | None = None,
        timeout: float = 10.0,
        max_retries: int = 2,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(timeout=timeout)
        self._owns_client = client is None
        self._max_retries = max_retries

    async def __aenter__(self) -> "OddsApiProvider":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def list_sports(self) -> list[str]:
        payload = await self._get("/sports")
        return self._string_list(payload)

    async def list_leagues(self, sport: str | None = None) -> list[str]:
        payload = await self._get("/leagues", params=self._optional_params(sport=sport))
        return self._string_list(payload)

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
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        payload = await self._get(
            "/events",
            params=self._optional_params(
                sport=sport,
                league=league,
                start_from=start_from,
                start_to=start_to,
                cursor=cursor,
                limit=limit,
            ),
        )
        items = payload.get("items", [])
        if not isinstance(items, list):
            raise ProviderError("Odds API returned an invalid events payload")
        return [self._event(item) for item in items], self._nullable_string(
            payload.get("next_cursor")
        )

    async def get_event(self, provider_event_id: str) -> ProviderEvent:
        payload = await self._get(f"/events/{provider_event_id}")
        data = payload.get("data", payload)
        if not isinstance(data, dict):
            raise ProviderError("Odds API returned an invalid event payload")
        data = {"event_id": provider_event_id, **data}
        return self._event(data)

    async def get_odds(
        self,
        provider_event_id: str,
        *,
        bookmakers: list[str] | None = None,
        market_keys: list[str] | None = None,
        limit: int = 2000,
        cursor: str | None = None,
    ) -> ProviderOddsSnapshot:
        if not 1 <= limit <= 10000:
            raise ValueError("limit must be between 1 and 10000")
        payload = await self._get(
            f"/events/{provider_event_id}/odds/snapshot",
            params=self._optional_params(
                bookmakers=",".join(bookmakers) if bookmakers else None,
                market_keys=",".join(market_keys) if market_keys else None,
                limit=limit,
                cursor=cursor,
            ),
        )
        raw_items = payload.get("items", [])
        if not isinstance(raw_items, list):
            raise ProviderError("Odds API returned an invalid odds payload")
        as_of = self._timestamp_ms(payload.get("as_of_ts_ms"))
        lines = tuple(self._odds_line(item, provider_event_id) for item in raw_items)
        return ProviderOddsSnapshot(
            provider_event_id=str(payload.get("event_id", provider_event_id)),
            as_of=as_of,
            lines=lines,
            next_cursor=self._nullable_string(payload.get("next_cursor")),
            resume=str(payload.get("resume", "")),
        )

    async def _get(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        request_params = {key: value for key, value in (params or {}).items() if value is not None}
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.get(
                    f"{self._base_url}{path}",
                    params=request_params,
                    headers={"X-API-Key": self._api_key},
                )
            except httpx.HTTPError as exc:
                if attempt >= self._max_retries:
                    raise ProviderUnavailable("Odds API request failed") from exc
                await asyncio.sleep(self._backoff(attempt))
                continue
            if response.status_code == 429:
                if attempt >= self._max_retries:
                    raise ProviderRateLimited("Odds API rate limit exceeded")
                await asyncio.sleep(self._retry_after(response, attempt))
                continue
            if response.status_code in {401, 403}:
                raise ProviderAuthenticationError("Odds API rejected the API key")
            if response.status_code == 404:
                raise ProviderNotFound("Odds API resource was not found")
            if response.status_code >= 500:
                if attempt >= self._max_retries:
                    raise ProviderUnavailable("Odds API is unavailable")
                await asyncio.sleep(self._backoff(attempt))
                continue
            if response.status_code >= 400:
                raise ProviderError(f"Odds API request failed with status {response.status_code}")
            payload = response.json()
            if not isinstance(payload, dict):
                raise ProviderError("Odds API returned a non-object JSON response")
            return payload
        raise ProviderUnavailable("Odds API request failed")

    @staticmethod
    def _optional_params(**params: Any) -> dict[str, Any]:
        return {key: value for key, value in params.items() if value is not None}

    @staticmethod
    def _string_list(payload: dict[str, Any]) -> list[str]:
        values = payload.get("items")
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            raise ProviderError("Odds API returned an invalid catalog payload")
        return values

    @staticmethod
    def _event(item: Any) -> ProviderEvent:
        if not isinstance(item, dict) or not item.get("event_id"):
            raise ProviderError("Odds API returned an invalid event item")
        start_time = item.get("start_time")
        return ProviderEvent(
            provider_event_id=str(item["event_id"]),
            sport=item.get("sport"),
            league=item.get("league"),
            start_time=(datetime.fromtimestamp(start_time, tz=UTC) if start_time else None),
            home_team=item.get("home_team"),
            away_team=item.get("away_team"),
        )

    @staticmethod
    def _odds_line(item: Any, provider_event_id: str) -> ProviderOddsLine:
        if not isinstance(item, dict) or not item.get("id") or not item.get("bookmaker"):
            raise ProviderError("Odds API returned an invalid odds line")
        line: Decimal | None = None
        try:
            if item.get("line") is not None:
                line = Decimal(str(item["line"]))
        except (InvalidOperation, TypeError):
            # Props may encode the side in the line field (for example,
            # ``over 39.5``); the side remains available in selection_name.
            line = None
        try:
            odds = Decimal(str(item["odds"])) if item.get("odds") is not None else None
        except (InvalidOperation, TypeError) as exc:
            raise ProviderError("Odds API returned a non-numeric price") from exc
        return ProviderOddsLine(
            id=str(item["id"]),
            provider_event_id=str(item.get("event_id", provider_event_id)),
            bookmaker=str(item["bookmaker"]),
            market_key=str(item.get("market_key", "")),
            selection=item.get("selection_name") or item.get("selection_key"),
            line=line,
            odds=odds,
            is_available=bool(item.get("is_available", True)),
        )

    @staticmethod
    def _nullable_string(value: Any) -> str | None:
        return str(value) if value is not None else None

    @staticmethod
    def _timestamp_ms(value: Any) -> datetime | None:
        return datetime.fromtimestamp(value / 1000, tz=UTC) if value else None

    @staticmethod
    def _backoff(attempt: int) -> float:
        return float(min(8.0, 0.5 * (2**attempt)) + random.uniform(0, 0.25))

    @classmethod
    def _retry_after(cls, response: httpx.Response, attempt: int) -> float:
        value = response.headers.get("Retry-After")
        if value:
            try:
                return max(0.0, float(value))
            except ValueError:
                try:
                    retry_at = parsedate_to_datetime(str(value))
                    return max(0.0, (retry_at - datetime.now(UTC)).total_seconds())
                except (TypeError, ValueError, OverflowError):
                    pass
        return cls._backoff(attempt)
