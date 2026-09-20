"""Favorite target types."""

from enum import StrEnum


class FavoriteType(StrEnum):
    """Supported favorite targets."""

    SPORT = "sport"
    LEAGUE = "league"
    TEAM = "team"
    EVENT = "event"
    PLAYER = "player"
