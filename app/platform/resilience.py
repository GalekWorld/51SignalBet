"""Lightweight circuit breaker for unstable external providers."""

from dataclasses import dataclass
from time import monotonic


class CircuitOpen(RuntimeError):
    pass


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    recovery_seconds: float = 30.0
    failures: int = 0
    opened_at: float | None = None

    def before_call(self) -> None:
        if self.opened_at is not None and monotonic() - self.opened_at < self.recovery_seconds:
            raise CircuitOpen("circuit is open")
        if self.opened_at is not None:
            self.failures = 0
            self.opened_at = None

    def success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.opened_at = monotonic()
