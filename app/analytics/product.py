"""Minimal product analytics events."""

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class ProductEvent:
    name: str
    user_id: str | None
    occurred_at: datetime
    properties: dict[str, str]


class ProductAnalytics:
    def __init__(self) -> None:
        self._events: list[ProductEvent] = []

    def record(
        self, name: str, *, user_id: str | None = None, properties: dict[str, str] | None = None
    ) -> ProductEvent:
        event = ProductEvent(name, user_id, datetime.now(UTC), properties or {})
        self._events.append(event)
        return event

    def snapshot(self) -> tuple[ProductEvent, ...]:
        return tuple(self._events)
