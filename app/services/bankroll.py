"""Ledger-backed virtual bankroll service."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Bankroll, BankrollTransaction
from app.domain.bankroll import BankrollTransactionType


class InvalidBankrollOperation(ValueError):
    """The requested virtual bankroll operation is invalid."""


class BankrollService:
    """Never mutate balance directly; every change is a ledger transaction."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create(self, user_id: UUID, *, currency: str = "EUR") -> Bankroll:
        bankroll = await self._session.scalar(select(Bankroll).where(Bankroll.user_id == user_id))
        if bankroll is None:
            bankroll = Bankroll(user_id=user_id, currency=currency.upper())
            self._session.add(bankroll)
            await self._session.flush()
        return bankroll

    async def balance(self, bankroll_id: UUID) -> Decimal:
        value = await self._session.scalar(
            select(func.coalesce(func.sum(BankrollTransaction.amount), 0)).where(
                BankrollTransaction.bankroll_id == bankroll_id
            )
        )
        return Decimal(str(value or 0))

    async def add_transaction(
        self,
        *,
        bankroll_id: UUID,
        transaction_type: BankrollTransactionType,
        amount: Decimal,
        idempotency_key: str,
        reference_id: str | None = None,
        description: str | None = None,
    ) -> BankrollTransaction:
        if amount == 0:
            raise InvalidBankrollOperation("transaction amount cannot be zero")
        bankroll = await self._session.scalar(
            select(Bankroll).where(Bankroll.id == bankroll_id).with_for_update()
        )
        if bankroll is None:
            raise InvalidBankrollOperation("bankroll does not exist")
        existing = await self._session.scalar(
            select(BankrollTransaction).where(
                BankrollTransaction.bankroll_id == bankroll_id,
                BankrollTransaction.idempotency_key == idempotency_key,
            )
        )
        if existing is not None:
            return existing
        if amount < 0 and await self.balance(bankroll_id) + amount < 0:
            raise InvalidBankrollOperation("insufficient virtual bankroll")
        transaction = BankrollTransaction(
            bankroll_id=bankroll_id,
            transaction_type=transaction_type,
            amount=amount,
            idempotency_key=idempotency_key,
            reference_id=reference_id,
            description=description,
        )
        self._session.add(transaction)
        await self._session.commit()
        return transaction
