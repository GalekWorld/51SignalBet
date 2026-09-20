"""Immutable administrative audit log."""

# ruff: noqa: F821
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.users import User

from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedModel


class AuditLog(TimestampedModel):
    __tablename__ = "audit_logs"

    actor_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False)
    data: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    actor: Mapped["User | None"] = relationship()
