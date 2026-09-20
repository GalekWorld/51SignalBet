"""Sports-domain enums and validation helpers."""

from enum import StrEnum


class EventStatus(StrEnum):
    """Lifecycle status supplied by a sports-data provider."""

    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class ParticipantType(StrEnum):
    """Types of participants that may be added in future phases."""

    TEAM = "team"
    PLAYER = "player"


def validate_event_participants(home_team_id: object, away_team_id: object) -> None:
    """Reject an event where both sides point at the same team."""

    if home_team_id == away_team_id:
        raise ValueError("home and away teams must be different")
