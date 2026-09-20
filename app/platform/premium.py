"""Advanced premium feature gating."""

from dataclasses import dataclass

from app.domain.subscriptions import Entitlement


@dataclass(frozen=True)
class PremiumFeature:
    key: str
    entitlement: Entitlement
    label: str


PREMIUM_FEATURES = (
    PremiumFeature("advanced_alerts", Entitlement.ADVANCED_ALERTS, "Alertas avanzadas"),
    PremiumFeature("public_history", Entitlement.PUBLIC_HISTORY, "Historial completo"),
)
