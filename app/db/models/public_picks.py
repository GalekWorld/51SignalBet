"""Immutable snapshots of opportunities published by the system."""

# ruff: noqa: F821
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.odds import Bookmaker
    from app.db.models.sports import Event

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedModel


class PublishedPick(TimestampedModel):
    __tablename__ = "published_picks"
    __table_args__ = (
        UniqueConstraint("publication_key", name="uq_published_picks_publication_key"),
    )

    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), nullable=False)
    bookmaker_id: Mapped[UUID] = mapped_column(ForeignKey("bookmakers.id"), nullable=False)
    market: Mapped[str] = mapped_column(String(150), nullable=False)
    selection: Mapped[str] = mapped_column(String(200), nullable=False)
    odds: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    fair_probability: Mapped[Decimal] = mapped_column(Numeric(12, 8), nullable=False)
    model_probability: Mapped[Decimal | None] = mapped_column(Numeric(12, 8), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    strategy_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    publication_key: Mapped[str] = mapped_column(String(255), nullable=False)

    event: Mapped["Event"] = relationship()
    bookmaker: Mapped["Bookmaker"] = relationship()
