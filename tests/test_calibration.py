from decimal import Decimal

from app.ml.calibration import BinnedCalibrator, CalibrationSample


def test_binned_calibrator_uses_empirical_hit_rate() -> None:
    calibrator = BinnedCalibrator(bins=2)
    calibrator.fit([CalibrationSample(Decimal(".2"), 0), CalibrationSample(Decimal(".3"), 1)])

    assert calibrator.calibrate(Decimal(".25")) == Decimal(".5")
