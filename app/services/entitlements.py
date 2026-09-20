"""Centralized subscription entitlement checks."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Subscription, User
from app.domain.admin import UserRole
from app.domain.subscriptions import PLAN_ENTITLEMENTS, Entitlement, SubscriptionPlan


class EntitlementService:
    """Resolve capabilities without scattering plan checks across interfaces."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def has(self, user_id: UUID, entitlement: Entitlement) -> bool:
        user = await self._session.scalar(select(User).where(User.id == user_id))
        if user is None:
            return False
        if user.role in {UserRole.ADMIN, UserRole.SUPERADMIN}:
            return True
        subscription = await self._session.scalar(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        plan = self._active_plan(subscription)
        return entitlement in PLAN_ENTITLEMENTS[plan]

    @staticmethod
    def _active_plan(subscription: Subscription | None) -> SubscriptionPlan:
        if subscription is None or not subscription.active:
            return SubscriptionPlan.FREE
        now = datetime.now(UTC)
        if subscription.ends_at is not None and subscription.ends_at <= now:
            return SubscriptionPlan.FREE
        return subscription.plan
