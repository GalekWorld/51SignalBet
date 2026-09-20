from datetime import UTC, datetime
from uuid import uuid4

import pytest
from app.db.base import Base
from app.db.models import Event
from app.domain.sports import EventStatus, validate_event_participants


def test_sports_tables_are_registered() -> None:
    assert {"sports", "leagues", "teams", "players", "events"} <= set(Base.metadata.tables)


def test_event_rejects_same_home_and_away_team() -> None:
    team_id = uuid4()

    with pytest.raises(ValueError, match="different"):
        validate_event_participants(team_id, team_id)


def test_event_uses_internal_uuid_and_timezone_aware_start() -> None:
    event = Event(
        provider="test",
        provider_event_id="event-1",
        sport_id=uuid4(),
        league_id=None,
        home_team_id=uuid4(),
        away_team_id=uuid4(),
        start_time=datetime(2026, 9, 20, 12, tzinfo=UTC),
        status=EventStatus.SCHEDULED,
    )

    assert Event.__table__.c.id.default is not None
    assert event.start_time.tzinfo is not None
    assert event.status == EventStatus.SCHEDULED
