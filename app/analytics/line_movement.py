"""Historical odds movement analysis independent from storage and transport."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class OddsPoint:
    """One time-stamped quote for the same selection."""

    bookmaker: str
    odds: Decimal
    timestamp: datetime


@dataclass(frozen=True)
class LineMovement:
    """Movement summary for one selection and analysis window."""

    opening_odds: Decimal
    current_odds: Decimal
    high: Decimal
    low: Decimal
    absolute_movement: Decimal
    percentage_movement: Decimal
    movement_over_period: Decimal
    movement_velocity_per_hour: Decimal
    cross_bookmaker_movement: dict[str, Decimal]
    outlier_bookmakers: tuple[str, ...]
    from_timestamp: datetime
    to_timestamp: datetime


class LineMovementService:
    """Calculate deterministic line movement metrics from ordered observations."""

    def analyze(
        self,
        points: list[OddsPoint],
        *,
        from_timestamp: datetime | None = None,
        to_timestamp: datetime | None = None,
        outlier_threshold: Decimal = Decimal("2"),
    ) -> LineMovement:
        if not points:
            raise ValueError("at least one odds point is required")
        if outlier_threshold <= Decimal("0"):
            raise ValueError("outlier_threshold must be positive")
        normalized = sorted(points, key=lambda point: point.timestamp)
        start = from_timestamp or normalized[0].timestamp
        end = to_timestamp or normalized[-1].timestamp
        window = [point for point in normalized if start <= point.timestamp <= end]
        if not window:
            raise ValueError("analysis window contains no odds points")
        opening = window[0].odds
        current = window[-1].odds
        movement = current - opening
        elapsed = (window[-1].timestamp - window[0].timestamp).total_seconds()
        velocity = movement / Decimal(str(elapsed / 3600)) if elapsed > 0 else Decimal("0")
        current_by_bookmaker = self._latest_by_bookmaker(window)
        median = self._median(list(current_by_bookmaker.values()))
        deviations = [abs(value - median) for value in current_by_bookmaker.values()]
        mad = self._median(deviations)
        outliers = tuple(
            sorted(
                bookmaker
                for bookmaker, value in current_by_bookmaker.items()
                if mad > 0 and abs(value - median) > outlier_threshold * mad
            )
        )
        return LineMovement(
            opening_odds=opening,
            current_odds=current,
            high=max(point.odds for point in window),
            low=min(point.odds for point in window),
            absolute_movement=movement,
            percentage_movement=movement / opening if opening else Decimal("0"),
            movement_over_period=movement,
            movement_velocity_per_hour=velocity,
            cross_bookmaker_movement={
                bookmaker: odds - self._first_for_bookmaker(window, bookmaker)
                for bookmaker, odds in current_by_bookmaker.items()
            },
            outlier_bookmakers=outliers,
            from_timestamp=start,
            to_timestamp=end,
        )

    @staticmethod
    def _latest_by_bookmaker(points: list[OddsPoint]) -> dict[str, Decimal]:
        latest: dict[str, Decimal] = {}
        for point in points:
            latest[point.bookmaker] = point.odds
        return latest

    @staticmethod
    def _first_for_bookmaker(points: list[OddsPoint], bookmaker: str) -> Decimal:
        for point in points:
            if point.bookmaker == bookmaker:
                return point.odds
        raise ValueError("bookmaker has no points")

    @staticmethod
    def _median(values: list[Decimal]) -> Decimal:
        ordered = sorted(values)
        middle = len(ordered) // 2
        if len(ordered) % 2:
            return ordered[middle]
        return (ordered[middle - 1] + ordered[middle]) / Decimal("2")
