"""Reusable bookmaker odds comparison service."""

from dataclasses import dataclass
from decimal import Decimal

from app.analytics.odds_math import InvalidOdds


@dataclass(frozen=True)
class BookmakerQuote:
    """One comparable quote for a market selection."""

    bookmaker: str
    odds: Decimal


@dataclass(frozen=True)
class SelectionComparison:
    """Summary statistics for one selection across bookmakers."""

    selection: str
    best_bookmaker: str
    best_odds: Decimal
    worst_odds: Decimal
    average_odds: Decimal
    median_odds: Decimal
    spread: Decimal
    bookmaker_count: int
    fair_odds: Decimal | None
    difference_vs_fair: Decimal | None


def _median(values: list[Decimal]) -> Decimal:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / Decimal("2")


class OddsComparisonService:
    """Compare quotes without depending on transport or persistence."""

    def compare(
        self,
        selection: str,
        quotes: list[BookmakerQuote],
        *,
        fair_odds: Decimal | None = None,
    ) -> SelectionComparison:
        """Calculate best, worst, mean, median and spread for one selection."""

        if not quotes:
            raise ValueError("at least one bookmaker quote is required")
        if any(quote.odds <= Decimal("1") for quote in quotes):
            raise InvalidOdds("decimal odds must be greater than 1")
        values = [quote.odds for quote in quotes]
        best_quote = max(quotes, key=lambda quote: quote.odds)
        difference = None
        if fair_odds is not None:
            if fair_odds <= Decimal("1"):
                raise InvalidOdds("fair odds must be greater than 1")
            difference = best_quote.odds / fair_odds - Decimal("1")
        return SelectionComparison(
            selection=selection,
            best_bookmaker=best_quote.bookmaker,
            best_odds=best_quote.odds,
            worst_odds=min(values),
            average_odds=sum(values, Decimal("0")) / len(values),
            median_odds=_median(values),
            spread=max(values) - min(values),
            bookmaker_count=len(values),
            fair_odds=fair_odds,
            difference_vs_fair=difference,
        )

    def compare_market(
        self,
        quotes_by_selection: dict[str, list[BookmakerQuote]],
        *,
        fair_odds_by_selection: dict[str, Decimal] | None = None,
    ) -> list[SelectionComparison]:
        """Compare all selections in stable input order."""

        fair_odds_by_selection = fair_odds_by_selection or {}
        return [
            self.compare(selection, quotes, fair_odds=fair_odds_by_selection.get(selection))
            for selection, quotes in quotes_by_selection.items()
        ]
