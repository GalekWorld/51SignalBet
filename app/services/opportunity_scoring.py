"""Transparent scoring of value opportunities."""

from dataclasses import dataclass
from decimal import Decimal

from app.services.value_engine import ValueOpportunity


@dataclass(frozen=True)
class OpportunityScore:
    """Score with explainable component values."""

    score: Decimal
    tier: str
    edge_component: Decimal
    value_component: Decimal
    coverage_component: Decimal
    freshness_component: Decimal


class OpportunityScorer:
    """Rank opportunities with bounded, configurable heuristics."""

    def __init__(
        self,
        *,
        max_edge: Decimal = Decimal("0.10"),
        max_expected_value: Decimal = Decimal("0.20"),
        target_bookmakers: int = 5,
        max_age_seconds: int = 600,
    ) -> None:
        if max_edge <= 0 or max_expected_value <= 0 or target_bookmakers < 1 or max_age_seconds < 1:
            raise ValueError("scoring limits must be positive")
        self._max_edge = max_edge
        self._max_ev = max_expected_value
        self._target_bookmakers = target_bookmakers
        self._max_age = max_age_seconds

    def score(
        self,
        opportunity: ValueOpportunity,
        *,
        bookmaker_count: int,
        age_seconds: int,
    ) -> OpportunityScore:
        if bookmaker_count < 0 or age_seconds < 0:
            raise ValueError("bookmaker_count and age_seconds cannot be negative")
        edge_component = self._bounded(opportunity.edge / self._max_edge)
        value_component = self._bounded(opportunity.expected_value / self._max_ev)
        coverage_component = self._bounded(Decimal(bookmaker_count) / self._target_bookmakers)
        freshness_component = self._bounded(Decimal(self._max_age - age_seconds) / self._max_age)
        score = (
            edge_component * 40
            + value_component * 35
            + coverage_component * 15
            + freshness_component * 10
        )
        score = score.quantize(Decimal("0.01"))
        tier = "high" if score >= 75 else "medium" if score >= 50 else "low"
        return OpportunityScore(
            score=score,
            tier=tier,
            edge_component=edge_component,
            value_component=value_component,
            coverage_component=coverage_component,
            freshness_component=freshness_component,
        )

    @staticmethod
    def _bounded(value: Decimal) -> Decimal:
        return max(Decimal("0"), min(Decimal("1"), value))
