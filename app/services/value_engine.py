"""Value opportunity engine independent from Telegram and persistence."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal

from app.analytics.odds_math import edge, expected_value
from app.services.odds_comparison import BookmakerQuote


@dataclass(frozen=True)
class ValueRules:
    """Configurable minimum quality thresholds for opportunities."""

    min_edge: Decimal = Decimal("0")
    min_expected_value: Decimal = Decimal("0")
    min_odds: Decimal = Decimal("1")


@dataclass(frozen=True)
class ValueOpportunity:
    """Immutable analytical output ready for API, alerts or persistence."""

    event_id: str
    market: str
    selection: str
    best_bookmaker: str
    best_odds: Decimal
    fair_probability: Decimal
    model_probability: Decimal | None
    edge: Decimal
    expected_value: Decimal
    detected_at: datetime
    reason: str
    metadata: dict[str, object] = field(default_factory=dict)


class ValueEngine:
    """Find opportunities from fair/model probabilities and bookmaker quotes."""

    def evaluate(
        self,
        *,
        event_id: str,
        market: str,
        selection: str,
        quotes: list[BookmakerQuote],
        fair_probability: Decimal,
        model_probability: Decimal | None = None,
        rules: ValueRules | None = None,
        detected_at: datetime | None = None,
    ) -> ValueOpportunity | None:
        """Return an opportunity only when all configured thresholds are met."""

        rules = rules or ValueRules()
        if not quotes:
            return None
        best = max(quotes, key=lambda quote: quote.odds)
        probability = model_probability if model_probability is not None else fair_probability
        calculated_edge = edge(probability, best.odds)
        calculated_ev = expected_value(probability, best.odds)
        if best.odds < rules.min_odds:
            return None
        if calculated_edge < rules.min_edge or calculated_ev < rules.min_expected_value:
            return None
        source = "model probability" if model_probability is not None else "fair probability"
        return ValueOpportunity(
            event_id=event_id,
            market=market,
            selection=selection,
            best_bookmaker=best.bookmaker,
            best_odds=best.odds,
            fair_probability=fair_probability,
            model_probability=model_probability,
            edge=calculated_edge,
            expected_value=calculated_ev,
            detected_at=(detected_at or datetime.now(UTC)).astimezone(UTC),
            reason=f"positive value from {source} at best available bookmaker",
            metadata={"bookmaker_count": len(quotes), "probability_source": source},
        )

    def evaluate_market(
        self,
        *,
        event_id: str,
        market: str,
        quotes_by_selection: dict[str, list[BookmakerQuote]],
        fair_probabilities: dict[str, Decimal],
        model_probabilities: dict[str, Decimal] | None = None,
        rules: ValueRules | None = None,
    ) -> list[ValueOpportunity]:
        """Evaluate all selections and preserve input order for stable output."""

        rules = rules or ValueRules()
        model_probabilities = model_probabilities or {}
        opportunities: list[ValueOpportunity] = []
        for selection, quotes in quotes_by_selection.items():
            fair_probability = fair_probabilities.get(selection)
            if fair_probability is None:
                continue
            opportunity = self.evaluate(
                event_id=event_id,
                market=market,
                selection=selection,
                quotes=quotes,
                fair_probability=fair_probability,
                model_probability=model_probabilities.get(selection),
                rules=rules,
            )
            if opportunity is not None:
                opportunities.append(opportunity)
        return opportunities
