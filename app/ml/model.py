"""First deterministic predictive baseline."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ModelFeatures:
    implied_probability: Decimal
    movement: Decimal = Decimal("0")
    hours_to_start: Decimal = Decimal("0")


class FirstPredictiveModel:
    """Transparent baseline adjusting market probability by movement."""

    name = "movement_adjusted_baseline"
    version = "1"

    def predict(self, features: ModelFeatures) -> Decimal:
        adjustment = -features.movement * Decimal("0.05")
        probability = features.implied_probability + adjustment
        return max(Decimal("0.001"), min(Decimal("0.999"), probability))
