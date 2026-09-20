from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.analytics.statistics import SettledBet, StatisticsService


def bets() -> list[SettledBet]:
    start = datetime(2026, 9, 20, tzinfo=UTC)
    return [
        SettledBet(
            start, "won", Decimal("2"), Decimal("10"), sport="football", edge=Decimal(".05")
        ),
        SettledBet(
            start + timedelta(hours=1), "lost", Decimal("3"), Decimal("10"), sport="football"
        ),
        SettledBet(start + timedelta(hours=2), "lost", Decimal("2"), Decimal("5"), sport="tennis"),
        SettledBet(
            start + timedelta(hours=3), "void", Decimal("2"), Decimal("10"), sport="football"
        ),
    ]


def test_statistics_distinguish_hit_rate_profit_roi_and_streaks() -> None:
    result = StatisticsService().calculate(bets())

    assert result.bets == 4
    assert result.wins == 1
    assert result.losses == 2
    assert result.voids == 1
    assert result.hit_rate == Decimal("1") / Decimal("3")
    assert result.profit == Decimal("-5")
    assert result.roi == Decimal("-5") / Decimal("25")
    assert result.winning_streak == 1
    assert result.losing_streak == 2
    assert result.max_drawdown == Decimal("15")


def test_statistics_can_group_by_sport() -> None:
    grouped = StatisticsService().group_by(bets(), "sport")

    assert set(grouped) == {"football", "tennis"}
    assert grouped["football"].bets == 3
