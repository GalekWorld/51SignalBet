from datetime import UTC, datetime
from decimal import Decimal

from app.services.odds_comparison import BookmakerQuote
from app.services.value_engine import ValueEngine, ValueRules


def test_value_engine_uses_best_bookmaker_and_fair_probability() -> None:
    detected = datetime(2026, 9, 20, 12, tzinfo=UTC)
    result = ValueEngine().evaluate(
        event_id="evt-1",
        market="MATCH_WINNER",
        selection="home",
        quotes=[
            BookmakerQuote("a", Decimal("2.00")),
            BookmakerQuote("b", Decimal("2.20")),
        ],
        fair_probability=Decimal("0.50"),
        rules=ValueRules(min_edge=Decimal("0.04"), min_expected_value=Decimal("0.05")),
        detected_at=detected,
    )

    assert result is not None
    assert result.best_bookmaker == "b"
    assert result.best_odds == Decimal("2.20")
    assert result.fair_probability == Decimal("0.50")
    assert result.model_probability is None
    assert result.edge == Decimal("0.0454545454545454545454545455")
    assert result.expected_value == Decimal("0.10")
    assert result.detected_at == detected


def test_model_probability_is_used_for_value_but_fair_probability_is_preserved() -> None:
    result = ValueEngine().evaluate(
        event_id="evt-1",
        market="TOTAL_GOALS",
        selection="over",
        quotes=[BookmakerQuote("a", Decimal("2.00"))],
        fair_probability=Decimal("0.50"),
        model_probability=Decimal("0.60"),
    )

    assert result is not None
    assert result.fair_probability == Decimal("0.50")
    assert result.model_probability == Decimal("0.60")
    assert result.expected_value == Decimal("0.20")


def test_thresholds_and_missing_fair_probability_filter_results() -> None:
    engine = ValueEngine()
    assert (
        engine.evaluate(
            event_id="evt-1",
            market="MATCH_WINNER",
            selection="home",
            quotes=[BookmakerQuote("a", Decimal("2.00"))],
            fair_probability=Decimal("0.50"),
            rules=ValueRules(min_edge=Decimal("0.10")),
        )
        is None
    )
    assert (
        engine.evaluate_market(
            event_id="evt-1",
            market="MATCH_WINNER",
            quotes_by_selection={"home": [BookmakerQuote("a", Decimal("2.00"))]},
            fair_probabilities={},
        )
        == []
    )
