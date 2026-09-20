from decimal import Decimal

from app.ml.model import FirstPredictiveModel, ModelFeatures
from app.ml.predictions import PredictionEngine


def test_prediction_preserves_model_and_feature_provenance() -> None:
    prediction = PredictionEngine().predict(
        event_id="evt-1",
        market="winner",
        selection="home",
        features=ModelFeatures(Decimal(".5")),
        feature_version="features-1",
        predictor=FirstPredictiveModel(),
    )

    assert prediction.model_name == "movement_adjusted_baseline"
    assert prediction.model_version == "1"
    assert prediction.feature_version == "features-1"
