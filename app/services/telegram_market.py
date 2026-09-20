"""Read-only market views used by the Telegram presentation layer."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.odds_math import de_vig
from app.db.models import Bookmaker, OddsSnapshot
from app.services.odds_comparison import BookmakerQuote, OddsComparisonService
from app.services.value_engine import ValueEngine, ValueOpportunity


@dataclass(frozen=True)
class QuoteView:
    """Compact quote data safe for a chat message."""

    market: str
    selection: str
    bookmaker: str
    odds: Decimal


class TelegramMarketService:
    """Load persisted odds and reuse analytical services for Telegram views."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def quotes(self, event_id: UUID, *, market: str | None = None) -> list[QuoteView]:
        statement = (
            select(OddsSnapshot, Bookmaker.name)
            .join(Bookmaker, Bookmaker.id == OddsSnapshot.bookmaker_id)
            .where(OddsSnapshot.event_id == event_id, OddsSnapshot.is_available.is_(True))
            .order_by(OddsSnapshot.market_key, OddsSnapshot.selection, OddsSnapshot.odds.desc())
            .limit(80)
        )
        if market is not None:
            statement = statement.where(OddsSnapshot.market_key == market)
        result = await self._session.execute(statement)
        return [
            QuoteView(
                market=row.OddsSnapshot.market_key,
                selection=row.OddsSnapshot.selection or "—",
                bookmaker=row.name,
                odds=row.OddsSnapshot.odds,
            )
            for row in result
            if row.OddsSnapshot.odds is not None and row.OddsSnapshot.odds > 1
        ]

    async def markets(self, event_id: UUID) -> list[str]:
        result = await self._session.scalars(
            select(OddsSnapshot.market_key)
            .where(OddsSnapshot.event_id == event_id, OddsSnapshot.is_available.is_(True))
            .distinct()
            .order_by(OddsSnapshot.market_key)
            .limit(20)
        )
        return list(result)

    async def opportunities(self, event_id: UUID) -> list[ValueOpportunity]:
        quotes = await self.quotes(event_id)
        grouped: dict[str, dict[str, list[BookmakerQuote]]] = {}
        for quote in quotes:
            grouped.setdefault(quote.market, {}).setdefault(quote.selection, []).append(
                BookmakerQuote(quote.bookmaker, quote.odds)
            )
        engine = ValueEngine()
        comparison = OddsComparisonService()
        opportunities: list[ValueOpportunity] = []
        for market, selections in grouped.items():
            prices = {
                selection: max(quote.odds for quote in values)
                for selection, values in selections.items()
            }
            try:
                fair_probabilities = de_vig(prices)
                comparison.compare_market(selections)
                opportunities.extend(
                    engine.evaluate_market(
                        event_id=str(event_id),
                        market=market,
                        quotes_by_selection=selections,
                        fair_probabilities=fair_probabilities,
                    )
                )
            except (ArithmeticError, ValueError):
                continue
        return opportunities
