from datetime import UTC, datetime
from decimal import Decimal

from app.analytics.strategies import StrategyContext, StrategyEngine, ThresholdValueStrategy
from app.services.value_engine import ValueOpportunity


def opportunity(edge: str) -> ValueOpportunity:
    return ValueOpportunity(
        event_id=edge,
        market="winner",
        selection="home",
        best_bookmaker="book",
        best_odds=Decimal("2"),
        fair_probability=Decimal(".5"),
        model_probability=None,
        edge=Decimal(edge),
        expected_value=Decimal(edge),
        detected_at=datetime.now(UTC),
        reason="test",
    )


def test_threshold_strategy_is_deterministic_and_versioned() -> None:
    strategy = ThresholdValueStrategy(min_edge=Decimal(".05"), min_score=Decimal("60"))
    selected = StrategyEngine().select(
        [
            (opportunity(".06"), StrategyContext(score=Decimal("60"))),
            (opportunity(".04"), StrategyContext(score=Decimal("90"))),
        ],
        strategy,
    )

    assert strategy.name == "threshold_value"
    assert strategy.version == "1"
    assert len(selected) == 1
