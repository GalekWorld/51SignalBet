import asyncio

from app.providers.contracts import ProviderEvent
from app.providers.errors import ProviderNotFound
from app.providers.fixture import FixtureOddsProvider


def test_second_provider_implements_the_same_contract() -> None:
    provider = FixtureOddsProvider(
        sports=["football"],
        leagues={"football": ["EPL"]},
        events=[ProviderEvent(provider_event_id="evt-1", sport="football", league="EPL")],
    )

    async def run() -> None:
        assert await provider.list_sports() == ["football"]
        events, cursor = await provider.list_events(sport="football")
        assert events[0].provider_event_id == "evt-1"
        assert cursor is None

    asyncio.run(run())


def test_fixture_provider_maps_missing_resources() -> None:
    provider = FixtureOddsProvider()

    async def run() -> None:
        try:
            await provider.get_event("missing")
        except ProviderNotFound:
            return
        raise AssertionError("missing fixture did not raise ProviderNotFound")

    asyncio.run(run())
