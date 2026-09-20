"""Immutable prediction generation."""

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Protocol

from app.ml.model import ModelFeatures


class Predictor(Protocol):
    name: str
    version: str

    def predict(self, features: ModelFeatures) -> Decimal: ...


@dataclass(frozen=True)
class Prediction:
    event_id: str
    market: str
    selection: str
    probability: Decimal
    model_name: str
    model_version: str
    feature_version: str
    predicted_at: datetime


class PredictionEngine:
    """Create predictions while preserving model and feature provenance."""

    def predict(
        self,
        *,
        event_id: str,
        market: str,
        selection: str,
        features: ModelFeatures,
        feature_version: str,
        predictor: Predictor,
        predicted_at: datetime | None = None,
    ) -> Prediction:
        return Prediction(
            event_id=event_id,
            market=market,
            selection=selection,
            probability=predictor.predict(features),
            model_name=predictor.name,
            model_version=predictor.version,
            feature_version=feature_version,
            predicted_at=(predicted_at or datetime.now(UTC)).astimezone(UTC),
        )
