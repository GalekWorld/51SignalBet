from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from app.analytics.line_movement import LineMovementService, OddsPoint


def test_line_movement_calculates_period_and_cross_bookmaker_metrics() -> None:
    start = datetime(2026, 9, 20, 12, tzinfo=UTC)
    result = LineMovementService().analyze(
        [
            OddsPoint("a", Decimal("2.00"), start),
            OddsPoint("b", Decimal("2.10"), start),
            OddsPoint("a", Decimal("2.20"), start + timedelta(hours=2)),
            OddsPoint("b", Decimal("2.05"), start + timedelta(hours=2)),
        ]
    )

    assert result.opening_odds == Decimal("2.00")
    assert result.current_odds == Decimal("2.05")
    assert result.high == Decimal("2.20")
    assert result.low == Decimal("2.00")
    assert result.absolute_movement == Decimal("0.05")
    assert result.percentage_movement == Decimal("0.025")
    assert result.movement_velocity_per_hour == Decimal("0.025")
    assert result.cross_bookmaker_movement == {"a": Decimal("0.20"), "b": Decimal("-0.05")}


def test_line_movement_supports_explicit_window() -> None:
    start = datetime(2026, 9, 20, 12, tzinfo=UTC)
    result = LineMovementService().analyze(
        [
            OddsPoint("a", Decimal("2.00"), start),
            OddsPoint("a", Decimal("1.90"), start + timedelta(hours=1)),
            OddsPoint("a", Decimal("1.80"), start + timedelta(hours=2)),
        ],
        from_timestamp=start + timedelta(hours=1),
    )

    assert result.opening_odds == Decimal("1.90")
    assert result.current_odds == Decimal("1.80")


def test_empty_movement_input_is_rejected() -> None:
    with pytest.raises(ValueError):
        LineMovementService().analyze([])
