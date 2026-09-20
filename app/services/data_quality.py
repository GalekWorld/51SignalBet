"""Data quality checks for provider odds and event data."""

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal


@dataclass(frozen=True)
class QualityObservation:
    """Input required for deterministic quality checks."""

    provider_timestamp: datetime | None
    received_timestamp: datetime
    odds: Decimal | None
    selection: str | None
    market_key: str | None
    mapping_conflict: bool = False
    result_missing: bool = False


@dataclass(frozen=True)
class QualityIssue:
    """One actionable quality issue."""

    code: str
    severity: str
    detail: str


class DataQualityService:
    """Detect stale, incomplete and anomalous observations before publication."""

    def __init__(
        self, *, stale_after_seconds: int = 300, max_provider_delay_seconds: int = 120
    ) -> None:
        if stale_after_seconds < 1 or max_provider_delay_seconds < 0:
            raise ValueError("quality thresholds are invalid")
        self._stale_after = stale_after_seconds
        self._max_delay = max_provider_delay_seconds

    def inspect(
        self,
        observation: QualityObservation,
        *,
        now: datetime | None = None,
    ) -> list[QualityIssue]:
        current = (now or datetime.now(UTC)).astimezone(UTC)
        issues: list[QualityIssue] = []
        if observation.provider_timestamp is None:
            issues.append(
                QualityIssue(
                    "missing_provider_timestamp", "degraded", "provider timestamp is absent"
                )
            )
        else:
            provider_ts = observation.provider_timestamp.astimezone(UTC)
            age = (current - provider_ts).total_seconds()
            if age > self._stale_after:
                issues.append(
                    QualityIssue(
                        "stale_odds", "reject", "odds are older than the freshness threshold"
                    )
                )
            delay = (observation.received_timestamp.astimezone(UTC) - provider_ts).total_seconds()
            if delay > self._max_delay:
                issues.append(
                    QualityIssue("provider_delay", "degraded", "provider data arrived late")
                )
            if delay < 0:
                issues.append(
                    QualityIssue(
                        "timestamp_anomaly",
                        "reject",
                        "received timestamp precedes provider timestamp",
                    )
                )
        if observation.odds is None or observation.odds <= Decimal("1"):
            issues.append(QualityIssue("invalid_odds", "reject", "odds are missing or invalid"))
        if not observation.market_key or not observation.selection:
            issues.append(
                QualityIssue("incomplete_market", "reject", "market or selection is missing")
            )
        if observation.mapping_conflict:
            issues.append(
                QualityIssue("mapping_conflict", "reject", "provider mapping needs review")
            )
        if observation.result_missing:
            issues.append(
                QualityIssue("missing_result", "degraded", "event result has not arrived")
            )
        return issues

    @staticmethod
    def is_publishable(issues: list[QualityIssue]) -> bool:
        """Reject observations carrying any reject-severity issue."""

        return not any(issue.severity == "reject" for issue in issues)
