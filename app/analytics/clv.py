"""Closing Line Value calculation with an explicit closing-price definition."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.analytics.odds_math import implied_probability


@dataclass(frozen=True)
class ClosingQuote:
    """Historical quote candidate for a selection."""

    bookmaker: str
    odds: Decimal
    timestamp: datetime
    is_available: bool = True


@dataclass(frozen=True)
class ClosingLineValue:
    """CLV result expressed as probability improvement."""

    pick_odds: Decimal
    closing_odds: Decimal
    pick_probability: Decimal
    closing_probability: Decimal
    clv: Decimal
    closing_timestamp: datetime
    bookmaker: str


class ClosingLineService:
    """Use the last available quote before event start as the closing price."""

    def calculate(
        self,
        *,
        pick_odds: Decimal,
        pick_timestamp: datetime,
        event_start: datetime,
        quotes: list[ClosingQuote],
        bookmaker: str | None = None,
    ) -> ClosingLineValue:
        """Calculate CLV without using quotes after kickoff or during suspension."""

        candidates = [
            quote
            for quote in quotes
            if quote.is_available
            and quote.timestamp <= event_start
            and quote.timestamp >= pick_timestamp
            and (bookmaker is None or quote.bookmaker == bookmaker)
        ]
        if not candidates:
            raise ValueError("no valid closing quote before event start")
        closing = max(candidates, key=lambda quote: quote.timestamp)
        pick_probability = implied_probability(pick_odds)
        closing_probability = implied_probability(closing.odds)
        return ClosingLineValue(
            pick_odds=pick_odds,
            closing_odds=closing.odds,
            pick_probability=pick_probability,
            closing_probability=closing_probability,
            clv=closing_probability - pick_probability,
            closing_timestamp=closing.timestamp,
            bookmaker=closing.bookmaker,
        )
