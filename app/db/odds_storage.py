"""Storage planning helpers for high-volume odds tables."""

from dataclasses import dataclass


@dataclass(frozen=True)
class OddsStoragePlan:
    partitioning_required: bool
    recommended_partition: str
    reason: str


def storage_plan(*, estimated_rows: int) -> OddsStoragePlan:
    if estimated_rows < 1:
        raise ValueError("estimated_rows must be positive")
    if estimated_rows < 10_000_000:
        return OddsStoragePlan(False, "none", "basic indexes are sufficient initially")
    return OddsStoragePlan(True, "monthly_provider_ts", "volume justifies time-based partitioning")
