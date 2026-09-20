import pytest
from app.ml.model import FirstPredictiveModel
from app.ml.registry import ModelRegistry


def test_registry_activates_explicit_model_version() -> None:
    registry = ModelRegistry()
    registry.register(FirstPredictiveModel(), name="baseline", version="1")
    registry.activate(name="baseline", version="1")

    assert registry.active("baseline").version == "1"


def test_registry_rejects_unknown_version() -> None:
    with pytest.raises(KeyError):
        ModelRegistry().activate(name="missing", version="1")
