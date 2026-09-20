"""Prediction-aware value engine extension."""

from decimal import Decimal

from app.ml.predictions import Prediction
from app.services.odds_comparison import BookmakerQuote
from app.services.value_engine import ValueEngine, ValueOpportunity, ValueRules


class ValueEngineV2:
    """Combine fair market probability, prediction and quality metadata."""

    def __init__(self) -> None:
        self._engine = ValueEngine()

    def evaluate(
        self,
        *,
        prediction: Prediction,
        fair_probability: Decimal,
        quotes: list[BookmakerQuote],
        rules: ValueRules | None = None,
        quality: dict[str, object] | None = None,
    ) -> ValueOpportunity | None:
        rules = rules or ValueRules()
        opportunity = self._engine.evaluate(
            event_id=prediction.event_id,
            market=prediction.market,
            selection=prediction.selection,
            quotes=quotes,
            fair_probability=fair_probability,
            model_probability=prediction.probability,
            rules=rules,
        )
        if opportunity is not None and quality:
            opportunity.metadata.update(
                {
                    "model_name": prediction.model_name,
                    "model_version": prediction.model_version,
                    **quality,
                }
            )
        return opportunity
