from datetime import UTC, datetime

from app.core.text import normalize_name
from app.providers.contracts import ProviderEvent
from app.services.event_ingestion import EventIngestionService


def test_normalize_name_handles_accents_and_spacing() -> None:
    assert normalize_name("  Atlético   Nacional ") == "atletico nacional"


def test_incomplete_provider_events_are_not_ingested() -> None:
    event = ProviderEvent(provider_event_id="evt-1")

    assert EventIngestionService._complete(event) is False


def test_complete_provider_event_is_valid_for_ingestion() -> None:
    event = ProviderEvent(
        provider_event_id="evt-1",
        sport="football",
        league="La Liga",
        start_time=datetime.now(UTC),
        home_team="Home",
        away_team="Away",
    )

    assert EventIngestionService._complete(event) is True
