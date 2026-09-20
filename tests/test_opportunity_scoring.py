from datetime import UTC, datetime
from decimal import Decimal

from app.services.opportunity_scoring import OpportunityScorer
from app.services.value_engine import ValueOpportunity


def opportunity() -> ValueOpportunity:
    return ValueOpportunity(
        event_id="evt-1",
        market="MATCH_WINNER",
        selection="home",
        best_bookmaker="bookmaker",
        best_odds=Decimal("2.20"),
        fair_probability=Decimal("0.50"),
        model_probability=None,
        edge=Decimal("0.05"),
        expected_value=Decimal("0.10"),
        detected_at=datetime.now(UTC),
        reason="test",
    )


def test_opportunity_score_is_bounded_and_explainable() -> None:
    result = OpportunityScorer().score(opportunity(), bookmaker_count=5, age_seconds=0)

    assert result.score == Decimal("62.50")
    assert result.tier == "medium"
    assert result.edge_component == Decimal("0.5")
    assert result.coverage_component == Decimal("1")


def test_stale_and_negative_inputs_are_handled() -> None:
    scorer = OpportunityScorer()
    result = scorer.score(opportunity(), bookmaker_count=0, age_seconds=10000)

    assert result.freshness_component == Decimal("0")
    assert result.score >= Decimal("0")
