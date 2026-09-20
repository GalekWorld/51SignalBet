from decimal import Decimal

import pytest
from app.analytics.odds_math import InvalidOdds
from app.services.odds_comparison import BookmakerQuote, OddsComparisonService


def test_comparison_calculates_requested_statistics() -> None:
    result = OddsComparisonService().compare(
        "home",
        [
            BookmakerQuote("a", Decimal("2.00")),
            BookmakerQuote("b", Decimal("2.20")),
            BookmakerQuote("c", Decimal("2.10")),
            BookmakerQuote("d", Decimal("1.90")),
        ],
        fair_odds=Decimal("2.00"),
    )

    assert result.best_bookmaker == "b"
    assert result.best_odds == Decimal("2.20")
    assert result.worst_odds == Decimal("1.90")
    assert result.average_odds == Decimal("2.05")
    assert result.median_odds == Decimal("2.05")
    assert result.spread == Decimal("0.30")
    assert result.bookmaker_count == 4
    assert result.difference_vs_fair == Decimal("0.10")


def test_market_comparison_preserves_selection_order() -> None:
    result = OddsComparisonService().compare_market(
        {
            "home": [BookmakerQuote("a", Decimal("2.00"))],
            "away": [BookmakerQuote("a", Decimal("3.00"))],
        }
    )

    assert [item.selection for item in result] == ["home", "away"]


def test_invalid_and_empty_quotes_are_rejected() -> None:
    with pytest.raises(ValueError):
        OddsComparisonService().compare("home", [])
    with pytest.raises(InvalidOdds):
        OddsComparisonService().compare("home", [BookmakerQuote("a", Decimal("1.00"))])
