import asyncio
from datetime import UTC
from decimal import Decimal

import httpx
import pytest
from app.providers.errors import ProviderAuthenticationError, ProviderRateLimited
from app.providers.odds_api import OddsApiProvider


def transport_for(handler):
    return httpx.MockTransport(handler)


def test_provider_uses_documented_auth_and_normalizes_events() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "event_id": "evt-1",
                        "sport": "football",
                        "league": "EPL",
                        "start_time": 1760000000,
                        "home_team": "Home",
                        "away_team": "Away",
                    }
                ],
                "next_cursor": None,
                "count": 1,
            },
            request=request,
        )

    client = httpx.AsyncClient(transport=transport_for(handler))
    provider = OddsApiProvider("secret", client=client, max_retries=0)

    async def run() -> tuple[list, str | None]:
        result = await provider.list_events(sport="football", limit=1)
        await client.aclose()
        return result

    events, next_cursor = asyncio.run(run())

    assert events[0].provider_event_id == "evt-1"
    assert events[0].start_time is not None
    assert events[0].start_time.tzinfo == UTC
    assert next_cursor is None
    assert requests[0].headers["X-API-Key"] == "secret"
    assert requests[0].url.params["sport"] == "football"


def test_provider_normalizes_decimal_odds() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "event_id": "evt-1",
                "as_of_ts_ms": 1760000000000,
                "items": [
                    {
                        "id": "line-1",
                        "event_id": "evt-1",
                        "bookmaker": "pinnacle",
                        "market_key": "moneyline",
                        "selection_name": "Home",
                        "odds": 2.15,
                        "line": None,
                        "is_available": True,
                    }
                ],
                "resume": "0-1",
            },
            request=request,
        )

    client = httpx.AsyncClient(transport=transport_for(handler))
    provider = OddsApiProvider("secret", client=client, max_retries=0)

    async def run():
        result = await provider.get_odds("evt-1")
        await client.aclose()
        return result

    snapshot = asyncio.run(run())

    assert snapshot.lines[0].odds == Decimal("2.15")
    assert snapshot.resume == "0-1"


def test_provider_accepts_textual_prop_lines() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "event_id": "evt-1",
                "items": [
                    {
                        "id": "line-1",
                        "event_id": "evt-1",
                        "bookmaker": "pinnacle",
                        "market_key": "player_props",
                        "selection_name": "over 39.5",
                        "odds": 1.91,
                        "line": "over 39.5",
                    }
                ],
            },
            request=request,
        )

    client = httpx.AsyncClient(transport=transport_for(handler))
    provider = OddsApiProvider("secret", client=client, max_retries=0)

    async def run():
        result = await provider.get_odds("evt-1")
        await client.aclose()
        return result

    snapshot = asyncio.run(run())

    assert snapshot.lines[0].line is None
    assert snapshot.lines[0].selection == "over 39.5"
    assert snapshot.lines[0].odds == Decimal("1.91")


def test_provider_maps_authentication_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, request=request)

    client = httpx.AsyncClient(transport=transport_for(handler))
    provider = OddsApiProvider("bad", client=client, max_retries=0)

    async def run() -> None:
        with pytest.raises(ProviderAuthenticationError):
            await provider.list_sports()
        await client.aclose()

    asyncio.run(run())


def test_provider_maps_rate_limit_after_retries() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, headers={"Retry-After": "0"}, request=request)

    client = httpx.AsyncClient(transport=transport_for(handler))
    provider = OddsApiProvider("secret", client=client, max_retries=0)

    async def run() -> None:
        with pytest.raises(ProviderRateLimited):
            await provider.list_sports()
        await client.aclose()

    asyncio.run(run())
