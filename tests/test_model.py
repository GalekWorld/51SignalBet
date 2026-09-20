from decimal import Decimal

from app.ml.model import FirstPredictiveModel, ModelFeatures


def test_first_predictive_model_is_bounded_and_versioned() -> None:
    model = FirstPredictiveModel()

    assert model.name == "movement_adjusted_baseline"
    assert model.version == "1"
    assert Decimal("0") < model.predict(ModelFeatures(Decimal(".5"))) < Decimal("1")
