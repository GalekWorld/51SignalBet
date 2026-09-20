"""Human-readable explanations for analytical outputs."""

from dataclasses import dataclass

from app.services.value_engine import ValueOpportunity


@dataclass(frozen=True)
class Explanation:
    """Neutral explanation with explicit evidence and caveats."""

    summary: str
    evidence: tuple[str, ...]
    caveats: tuple[str, ...]


class OpportunityExplainer:
    """Explain opportunity inputs without promotional or guaranteed language."""

    def explain(self, opportunity: ValueOpportunity) -> Explanation:
        source = "model" if opportunity.model_probability is not None else "fair market"
        evidence = (
            f"best odds {opportunity.best_odds} at {opportunity.best_bookmaker}",
            f"edge {opportunity.edge:.4f}",
            f"expected value {opportunity.expected_value:.4f}",
            f"probability source: {source}",
        )
        return Explanation(
            summary=f"{opportunity.selection} shows an analytical value signal from {source} probability.",
            evidence=evidence,
            caveats=(
                "Probabilities are estimates, not guarantees.",
                "Prices and market availability can change.",
            ),
        )
