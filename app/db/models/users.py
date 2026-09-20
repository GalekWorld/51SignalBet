"""Persistence model for Telegram users."""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import TimestampedModel
from app.domain.admin import UserRole


class User(TimestampedModel):
    """Internal user identity linked to Telegram, not to a bookmaker account."""

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("telegram_user_id", name="uq_users_telegram_user_id"),)

    telegram_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(String(20), default=UserRole.USER, nullable=False)
