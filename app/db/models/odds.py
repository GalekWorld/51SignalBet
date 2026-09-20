"""Append-only persistence models for bookmaker odds snapshots."""

# ruff: noqa: F821
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.sports import Event

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedModel


class Bookmaker(TimestampedModel):
    """Internal bookmaker identity, independent from provider IDs."""

    __tablename__ = "bookmakers"

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    snapshots: Mapped[list["OddsSnapshot"]] = relationship(back_populates="bookmaker")


class OddsSnapshot(TimestampedModel):
    """One observed price state; rows are never updated by ingestion."""

    __tablename__ = "odds_snapshots"
    __table_args__ = (
        Index(
            "ix_odds_snapshots_event_market_provider_ts", "event_id", "market_key", "provider_ts"
        ),
        Index("ix_odds_snapshots_bookmaker_provider_ts", "bookmaker_id", "provider_ts"),
        UniqueConstraint(
            "provider",
            "provider_line_id",
            "provider_ts",
            name="uq_odds_snapshots_provider_line_ts",
        ),
    )

    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), nullable=False)
    bookmaker_id: Mapped[UUID] = mapped_column(ForeignKey("bookmakers.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_line_id: Mapped[str] = mapped_column(String(500), nullable=False)
    market_key: Mapped[str] = mapped_column(String(500), nullable=False)
    selection: Mapped[str | None] = mapped_column(String(200), nullable=True)
    line: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    odds: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    provider_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False)

    event: Mapped["Event"] = relationship()
    bookmaker: Mapped[Bookmaker] = relationship(back_populates="snapshots")
