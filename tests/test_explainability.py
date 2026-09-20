from datetime import UTC, datetime
from decimal import Decimal

from app.services.explainability import OpportunityExplainer
from app.services.value_engine import ValueOpportunity


def test_explanation_is_neutral_and_evidence_based() -> None:
    opportunity = ValueOpportunity(
        "evt-1",
        "winner",
        "home",
        "book",
        Decimal("2.2"),
        Decimal(".5"),
        Decimal(".6"),
        Decimal(".1"),
        Decimal(".32"),
        datetime.now(UTC),
        "reason",
    )
    explanation = OpportunityExplainer().explain(opportunity)

    assert "guarantee" not in explanation.summary.lower()
    assert len(explanation.evidence) == 4
    assert explanation.caveats
