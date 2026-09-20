"""Quiet-hours aware smart notification policy."""

from dataclasses import dataclass
from datetime import datetime, time


@dataclass(frozen=True)
class NotificationPolicy:
    quiet_start: time | None = None
    quiet_end: time | None = None
    minimum_score: int = 0

    def allows(self, *, local_time: datetime, score: int) -> bool:
        if score < self.minimum_score:
            return False
        if self.quiet_start is None or self.quiet_end is None:
            return True
        current = local_time.time()
        if self.quiet_start <= self.quiet_end:
            return not self.quiet_start <= current < self.quiet_end
        return not (current >= self.quiet_start or current < self.quiet_end)
