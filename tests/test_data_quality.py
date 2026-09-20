from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.services.data_quality import DataQualityService, QualityObservation


def test_quality_detects_stale_and_incomplete_odds() -> None:
    now = datetime(2026, 9, 20, 12, tzinfo=UTC)
    issues = DataQualityService(stale_after_seconds=300).inspect(
        QualityObservation(
            provider_timestamp=now - timedelta(minutes=10),
            received_timestamp=now,
            odds=None,
            selection=None,
            market_key="moneyline",
        ),
        now=now,
    )

    codes = {issue.code for issue in issues}
    assert {"stale_odds", "invalid_odds", "incomplete_market"} <= codes
    assert not DataQualityService.is_publishable(issues)


def test_quality_accepts_fresh_complete_observation() -> None:
    now = datetime(2026, 9, 20, 12, tzinfo=UTC)
    issues = DataQualityService().inspect(
        QualityObservation(now - timedelta(seconds=10), now, Decimal("2.10"), "Home", "moneyline"),
        now=now,
    )

    assert issues == []
    assert DataQualityService.is_publishable(issues)
