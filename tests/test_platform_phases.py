import hashlib
import hmac
from datetime import UTC, datetime, time
from decimal import Decimal

import pytest
from app.analytics.charts import ChartPoint, odds_series
from app.analytics.product import ProductAnalytics
from app.compliance.responsible_gambling import responsible_message
from app.platform.resilience import CircuitBreaker, CircuitOpen
from app.security.signatures import verify_signature
from app.services.notifications import NotificationPolicy


def test_later_platform_features_are_bounded_and_safe() -> None:
    now = datetime(2026, 9, 20, 23, 0, tzinfo=UTC)
    policy = NotificationPolicy(time(22), time(7), minimum_score=70)
    assert not policy.allows(local_time=now, score=90)
    assert odds_series([ChartPoint(now, Decimal("2"))])
    assert responsible_message()
    analytics = ProductAnalytics()
    analytics.record("opened_event", user_id="u1")
    assert len(analytics.snapshot()) == 1


def test_resilience_and_signature_helpers() -> None:
    breaker = CircuitBreaker(failure_threshold=1, recovery_seconds=60)
    breaker.failure()
    with pytest.raises(CircuitOpen):
        breaker.before_call()
    assert verify_signature(b"payload", "", "secret") is False
    signature = hmac.new(b"secret", b"payload", hashlib.sha256).hexdigest()
    assert verify_signature(b"payload", signature, "secret") is True
