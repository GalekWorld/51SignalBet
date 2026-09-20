"""Bet tracking concepts."""

from enum import StrEnum


class BetStatus(StrEnum):
    """Settlement lifecycle for a tracked virtual bet."""

    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    VOID = "void"
    PUSH = "push"
    CANCELLED = "cancelled"
