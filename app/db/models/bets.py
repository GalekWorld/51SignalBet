"""Persistence model for tracked virtual bets."""

# ruff: noqa: F821
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.odds import Bookmaker
    from app.db.models.sports import Event
    from app.db.models.users import User

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedModel
from app.domain.bets import BetStatus


class BetRecord(TimestampedModel):
    __tablename__ = "bet_records"
    __table_args__ = (
        UniqueConstraint("user_id", "idempotency_key", name="uq_bet_records_user_idempotency"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), nullable=False)
    bookmaker_id: Mapped[UUID | None] = mapped_column(ForeignKey("bookmakers.id"), nullable=True)
    market: Mapped[str] = mapped_column(String(150), nullable=False)
    selection: Mapped[str] = mapped_column(String(200), nullable=False)
    odds: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    stake: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    units: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[BetStatus] = mapped_column(String(20), default=BetStatus.PENDING, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)

    user: Mapped["User"] = relationship()
    event: Mapped["Event"] = relationship()
    bookmaker: Mapped["Bookmaker | None"] = relationship()
