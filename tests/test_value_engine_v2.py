from decimal import Decimal

from app.ml.model import FirstPredictiveModel, ModelFeatures
from app.ml.predictions import PredictionEngine
from app.services.odds_comparison import BookmakerQuote
from app.services.value_engine import ValueRules
from app.services.value_engine_v2 import ValueEngineV2


def test_value_engine_v2_keeps_prediction_provenance() -> None:
    prediction = PredictionEngine().predict(
        event_id="evt-1",
        market="winner",
        selection="home",
        features=ModelFeatures(Decimal(".6")),
        feature_version="f1",
        predictor=FirstPredictiveModel(),
    )
    result = ValueEngineV2().evaluate(
        prediction=prediction,
        fair_probability=Decimal(".5"),
        quotes=[BookmakerQuote("book", Decimal("2"))],
        rules=ValueRules(min_expected_value=Decimal(".01")),
        quality={"fresh": True},
    )

    assert result is not None
    assert result.metadata["model_version"] == "1"
    assert result.metadata["fresh"] is True
