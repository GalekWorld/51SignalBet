from decimal import Decimal
from uuid import uuid4

from app.db.models import AlertRule
from app.domain.alerts import AlertMetric, AlertOperator
from app.services.alerts import AlertInput, matches


def rule(**kwargs) -> AlertRule:
    return AlertRule(
        id=uuid4(),
        user_id=uuid4(),
        metric=kwargs.get("metric", AlertMetric.EDGE),
        operator=kwargs.get("operator", AlertOperator.GREATER_EQUAL),
        threshold=kwargs.get("threshold", Decimal("0.05")),
        filters=kwargs.get("filters", {}),
        cooldown_seconds=3600,
        enabled=True,
    )


def test_alert_matches_metric_and_filter() -> None:
    assert matches(
        rule(filters={"market": "MATCH_WINNER"}),
        AlertInput("evt:home", edge=Decimal("0.06"), dimensions={"market": "MATCH_WINNER"}),
    )
    assert not matches(
        rule(filters={"market": "MATCH_WINNER"}),
        AlertInput("evt:home", edge=Decimal("0.06"), dimensions={"market": "TOTAL_GOALS"}),
    )


def test_alert_supports_upper_and_lower_thresholds() -> None:
    assert matches(
        rule(metric=AlertMetric.ODDS, operator=AlertOperator.LESS_EQUAL, threshold=Decimal("2.00")),
        AlertInput("evt:home", odds=Decimal("1.95")),
    )
