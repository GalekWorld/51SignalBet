"""Persistence model for entitlement subscriptions."""

# ruff: noqa: F821
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.users import User

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedModel
from app.domain.subscriptions import SubscriptionPlan


class Subscription(TimestampedModel):
    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("user_id", name="uq_subscriptions_user_id"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    plan: Mapped[SubscriptionPlan] = mapped_column(
        String(20), default=SubscriptionPlan.FREE, nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship()
