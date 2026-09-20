from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from app.analytics.backtester import BacktestBet, BacktestEngine


def test_backtester_simulates_bankroll_in_strict_temporal_order() -> None:
    start = datetime(2026, 9, 20, tzinfo=UTC)
    result = BacktestEngine().run(
        [
            BacktestBet(
                "evt-1",
                start,
                start,
                start + timedelta(hours=1),
                Decimal("2"),
                Decimal("10"),
                "won",
            ),
            BacktestBet(
                "evt-2",
                start + timedelta(hours=2),
                start + timedelta(hours=1),
                start + timedelta(hours=3),
                Decimal("2"),
                Decimal("10"),
                "lost",
            ),
        ],
        initial_bankroll=Decimal("100"),
    )

    assert result.final_bankroll == Decimal("100")
    assert result.executed == 2
    assert result.profit == Decimal("0")
    assert result.max_drawdown == Decimal("10")


def test_backtester_rejects_lookahead() -> None:
    start = datetime(2026, 9, 20, tzinfo=UTC)
    bet = BacktestBet(
        "evt-1",
        start,
        start + timedelta(minutes=1),
        start + timedelta(hours=1),
        Decimal("2"),
        Decimal("10"),
        "won",
    )

    with pytest.raises(ValueError, match="lookahead"):
        BacktestEngine().run([bet], initial_bankroll=Decimal("100"))
