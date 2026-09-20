from app.domain.subscriptions import PLAN_ENTITLEMENTS, Entitlement, SubscriptionPlan


def test_free_and_premium_plans_are_centralized() -> None:
    assert Entitlement.TODAY_EVENTS in PLAN_ENTITLEMENTS[SubscriptionPlan.FREE]
    assert Entitlement.ADVANCED_ALERTS not in PLAN_ENTITLEMENTS[SubscriptionPlan.FREE]
    assert Entitlement.ADVANCED_ALERTS in PLAN_ENTITLEMENTS[SubscriptionPlan.PREMIUM]
