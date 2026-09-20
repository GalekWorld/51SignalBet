"""Composable strategy abstractions for research and backtesting."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from app.services.value_engine import ValueOpportunity


@dataclass(frozen=True)
class StrategyContext:
    """Point-in-time context available to a strategy."""

    event_start_timestamp: int | None = None
    score: Decimal | None = None


class Strategy(Protocol):
    """Minimal strategy contract with no provider or database dependency."""

    name: str
    version: str

    def select(self, opportunity: ValueOpportunity, context: StrategyContext) -> bool: ...


@dataclass(frozen=True)
class ThresholdValueStrategy:
    """Select opportunities above explicit edge and optional score thresholds."""

    min_edge: Decimal = Decimal("0")
    min_score: Decimal | None = None
    name: str = "threshold_value"
    version: str = "1"

    def __post_init__(self) -> None:
        if self.min_edge < 0 or (self.min_score is not None and not 0 <= self.min_score <= 100):
            raise ValueError("strategy thresholds are invalid")

    def select(self, opportunity: ValueOpportunity, context: StrategyContext) -> bool:
        """Evaluate only information present at the strategy decision time."""

        if opportunity.edge < self.min_edge:
            return False
        return self.min_score is None or (
            context.score is not None and context.score >= self.min_score
        )


class StrategyEngine:
    """Apply a named strategy to an ordered opportunity stream."""

    def select(
        self,
        opportunities: list[tuple[ValueOpportunity, StrategyContext]],
        strategy: Strategy,
    ) -> list[ValueOpportunity]:
        return [
            opportunity
            for opportunity, context in opportunities
            if strategy.select(opportunity, context)
        ]
