import asyncio

from app.providers.sports_data import EventResult
from app.providers.sports_fixture import FixtureSportsDataProvider


def test_sports_data_provider_exposes_normalized_results() -> None:
    provider = FixtureSportsDataProvider(
        sports=["football"],
        leagues={"football": ["EPL"]},
        results={
            "evt-1": EventResult(
                provider_event_id="evt-1", status="finished", home_score=2, away_score=1
            )
        },
    )

    async def run() -> None:
        result = await provider.get_event_result("evt-1")
        assert result.status == "finished"
        assert result.home_score == 2

    asyncio.run(run())
