"""Simple empirical probability calibration."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CalibrationSample:
    predicted: Decimal
    outcome: int


class BinnedCalibrator:
    """Map predictions to empirical hit rates in fixed probability bins."""

    def __init__(self, *, bins: int = 10) -> None:
        if bins < 2:
            raise ValueError("bins must be at least 2")
        self._bins = bins
        self._rates: dict[int, Decimal] = {}

    def fit(self, samples: list[CalibrationSample]) -> None:
        grouped: dict[int, list[int]] = {}
        for sample in samples:
            if not 0 <= sample.predicted <= 1 or sample.outcome not in {0, 1}:
                raise ValueError("invalid calibration sample")
            index = min(self._bins - 1, int(sample.predicted * self._bins))
            grouped.setdefault(index, []).append(sample.outcome)
        self._rates = {
            index: Decimal(sum(values)) / len(values) for index, values in grouped.items()
        }

    def calibrate(self, predicted: Decimal) -> Decimal:
        if not 0 <= predicted <= 1:
            raise ValueError("predicted probability must be between 0 and 1")
        index = min(self._bins - 1, int(predicted * self._bins))
        return self._rates.get(index, predicted)
