"""Neutral messaging and voluntary user controls."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResponsibleLimits:
    max_daily_stake: int | None = None
    alerts_enabled: bool = True
    quiet_hours_enabled: bool = False


def responsible_message() -> str:
    return "Las probabilidades son estimaciones. No existen ganancias garantizadas."
