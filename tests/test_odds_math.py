from decimal import Decimal

import pytest
from app.analytics.odds_math import (
    InsufficientOutcomes,
    InvalidOdds,
    de_vig,
    edge,
    expected_value,
    fair_odds_for_market,
    implied_probability,
    overround,
)


def test_implied_probability_uses_decimal_arithmetic() -> None:
    assert implied_probability("2.00") == Decimal("0.5")


def test_overround_and_proportional_de_vig() -> None:
    odds = {"home": Decimal("2.00"), "draw": Decimal("3.50"), "away": Decimal("4.00")}

    assert overround(odds) == Decimal("0.035714285714285714285714286")
    fair = de_vig(odds)
    assert sum(fair.values(), Decimal("0")) == Decimal("1")
    assert fair["home"] > fair["away"]


def test_fair_odds_are_based_on_complete_market() -> None:
    fair = fair_odds_for_market({"home": "2.00", "away": "2.00"})

    assert fair["home"] == Decimal("2")
    assert fair["away"] == Decimal("2")


def test_edge_and_expected_value_are_distinct_metrics() -> None:
    assert edge("0.55", "2.00") == Decimal("0.05")
    assert expected_value("0.55", "2.00") == Decimal("0.10")


def test_invalid_market_is_rejected() -> None:
    with pytest.raises(InvalidOdds):
        implied_probability("1.00")
    with pytest.raises(InsufficientOutcomes):
        overround({"home": "2.00"})
