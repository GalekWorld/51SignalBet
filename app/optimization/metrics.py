"""Measurement primitives for post-launch optimization."""

from dataclasses import dataclass


@dataclass(frozen=True)
class QueryMetric:
    name: str
    duration_ms: float
    rows: int


def prioritize(metrics: list[QueryMetric]) -> list[QueryMetric]:
    return sorted(
        metrics, key=lambda metric: metric.duration_ms * max(metric.rows, 1), reverse=True
    )
