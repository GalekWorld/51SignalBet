"""Point-in-time feature engineering for future predictive models."""

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from app.analytics.odds_math import implied_probability


@dataclass(frozen=True)
class FeatureObservation:
    """Raw information available at a specific point in time."""

    odds: Decimal
    observed_at: datetime
    event_start: datetime
    opening_odds: Decimal | None = None
    bookmaker_count: int = 1


@dataclass(frozen=True)
class FeatureVector:
    """Versioned numeric features with their information cutoff."""

    feature_version: str
    as_of: datetime
    implied_probability: Decimal
    hours_to_start: Decimal
    movement: Decimal
    bookmaker_count: int
    freshness_seconds: Decimal


class FeaturePipeline:
    """Build only features known at or before the requested cutoff."""

    def __init__(self, *, feature_version: str = "1") -> None:
        self._version = feature_version

    def build(self, observation: FeatureObservation, *, as_of: datetime) -> FeatureVector:
        cutoff = as_of.astimezone(UTC)
        observed_at = observation.observed_at.astimezone(UTC)
        event_start = observation.event_start.astimezone(UTC)
        if observed_at > cutoff:
            raise ValueError("observation is in the future relative to as_of")
        if observation.bookmaker_count < 1:
            raise ValueError("bookmaker_count must be positive")
        movement = Decimal("0")
        if observation.opening_odds is not None:
            movement = observation.odds - observation.opening_odds
        return FeatureVector(
            feature_version=self._version,
            as_of=cutoff,
            implied_probability=implied_probability(observation.odds),
            hours_to_start=Decimal(str((event_start - cutoff).total_seconds() / 3600)),
            movement=movement,
            bookmaker_count=observation.bookmaker_count,
            freshness_seconds=Decimal(str((cutoff - observed_at).total_seconds())),
        )
