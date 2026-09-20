"""Persistence model for user favorites."""

# ruff: noqa: F821
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.users import User

from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import TimestampedModel
from app.domain.favorites import FavoriteType


class Favorite(TimestampedModel):
    """Polymorphic favorite reference with explicit target type."""

    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "favorite_type", "target_id", name="uq_favorites_user_type_target"
        ),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    favorite_type: Mapped[FavoriteType] = mapped_column(String(20), nullable=False)
    target_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)

    user: Mapped["User"] = relationship()
