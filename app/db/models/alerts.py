"""Persistence models for alert rules and trigger history."""

# ruff: noqa: F821
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.users import User

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedModel
from app.domain.alerts import AlertMetric, AlertOperator


class AlertRule(TimestampedModel):
    __tablename__ = "alert_rules"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    metric: Mapped[AlertMetric] = mapped_column(String(30), nullable=False)
    operator: Mapped[AlertOperator] = mapped_column(String(10), nullable=False)
    threshold: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    filters: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, default=3600, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship()
    events: Mapped[list["AlertEvent"]] = relationship(back_populates="rule")


class AlertEvent(TimestampedModel):
    __tablename__ = "alert_events"
    __table_args__ = (
        UniqueConstraint("rule_id", "dedup_key", name="uq_alert_events_rule_dedup_key"),
    )

    rule_id: Mapped[UUID] = mapped_column(ForeignKey("alert_rules.id"), nullable=False)
    dedup_key: Mapped[str] = mapped_column(String(255), nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    rule: Mapped[AlertRule] = relationship(back_populates="events")
