"""Chart-ready time series transformations."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class ChartPoint:
    timestamp: datetime
    value: Decimal


def odds_series(points: list[ChartPoint], *, limit: int = 500) -> list[ChartPoint]:
    """Return ordered, bounded points for a chart without changing source data."""

    if not 1 <= limit <= 5000:
        raise ValueError("chart limit is invalid")
    return sorted(points, key=lambda point: point.timestamp)[-limit:]
