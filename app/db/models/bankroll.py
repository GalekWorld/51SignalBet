"""Virtual bankroll ledger persistence models."""

# ruff: noqa: F821
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.users import User

from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedModel
from app.domain.bankroll import BankrollTransactionType


class Bankroll(TimestampedModel):
    __tablename__ = "bankrolls"
    __table_args__ = (UniqueConstraint("user_id", name="uq_bankrolls_user_id"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)

    user: Mapped["User"] = relationship()
    transactions: Mapped[list["BankrollTransaction"]] = relationship(back_populates="bankroll")


class BankrollTransaction(TimestampedModel):
    __tablename__ = "bankroll_transactions"
    __table_args__ = (
        UniqueConstraint(
            "bankroll_id", "idempotency_key", name="uq_bankroll_transactions_idempotency"
        ),
    )

    bankroll_id: Mapped[UUID] = mapped_column(ForeignKey("bankrolls.id"), nullable=False)
    transaction_type: Mapped[BankrollTransactionType] = mapped_column(String(30), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    bankroll: Mapped[Bankroll] = relationship(back_populates="transactions")
