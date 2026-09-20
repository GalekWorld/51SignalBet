"""Subscription plans and product entitlements."""

from enum import StrEnum


class SubscriptionPlan(StrEnum):
    FREE = "free"
    PREMIUM = "premium"
    ADMIN = "admin"


class Entitlement(StrEnum):
    TODAY_EVENTS = "today_events"
    BASIC_HISTORY = "basic_history"
    VALUE_OPPORTUNITIES = "value_opportunities"
    ADVANCED_ALERTS = "advanced_alerts"
    PUBLIC_HISTORY = "public_history"


PLAN_ENTITLEMENTS: dict[SubscriptionPlan, frozenset[Entitlement]] = {
    SubscriptionPlan.FREE: frozenset({Entitlement.TODAY_EVENTS, Entitlement.BASIC_HISTORY}),
    SubscriptionPlan.PREMIUM: frozenset(Entitlement),
    SubscriptionPlan.ADMIN: frozenset(Entitlement),
}
