from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from app.analytics.features import FeatureObservation, FeaturePipeline


def test_feature_pipeline_is_point_in_time_safe() -> None:
    as_of = datetime(2026, 9, 20, 12, tzinfo=UTC)
    vector = FeaturePipeline().build(
        FeatureObservation(
            Decimal("2"),
            as_of - timedelta(minutes=5),
            as_of + timedelta(hours=2),
            Decimal("2.2"),
            3,
        ),
        as_of=as_of,
    )

    assert vector.implied_probability == Decimal("0.5")
    assert vector.hours_to_start == Decimal("2")
    assert vector.movement == Decimal("-0.2")
    assert vector.freshness_seconds == Decimal("300.0")


def test_future_observation_is_rejected() -> None:
    as_of = datetime(2026, 9, 20, 12, tzinfo=UTC)
    with pytest.raises(ValueError, match="future"):
        FeaturePipeline().build(
            FeatureObservation(Decimal("2"), as_of + timedelta(seconds=1), as_of),
            as_of=as_of,
        )
