"""Settlement history for tracked bets."""

# ruff: noqa: F821
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.bets import BetRecord

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedModel


class SettlementEvent(TimestampedModel):
    __tablename__ = "settlement_events"
    __table_args__ = (UniqueConstraint("bet_id", name="uq_settlement_events_bet_id"),)

    bet_id: Mapped[UUID] = mapped_column(ForeignKey("bet_records.id"), nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    settled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payout_amount: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)

    bet: Mapped["BetRecord"] = relationship()
