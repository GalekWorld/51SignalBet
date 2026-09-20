"""Idempotent settlement of tracked virtual bets."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Bankroll, BankrollTransaction, BetRecord, SettlementEvent
from app.domain.bankroll import BankrollTransactionType
from app.domain.bets import BetStatus


class SettlementConflict(ValueError):
    """A bet cannot be settled with the requested result."""


def payout_for_result(status: BetStatus, stake: Decimal, odds: Decimal) -> Decimal:
    """Return the ledger credit required after a stake was already debited."""

    if status == BetStatus.WON:
        return stake * odds
    if status in {BetStatus.VOID, BetStatus.PUSH}:
        return stake
    return Decimal("0")


class SettlementService:
    """Settle once, credit the ledger when required, and preserve history."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def settle(self, bet_id: UUID, result: BetStatus) -> SettlementEvent:
        if result not in {BetStatus.WON, BetStatus.LOST, BetStatus.VOID, BetStatus.PUSH}:
            raise SettlementConflict("bet result is not settleable")
        existing_settlement = await self._session.scalar(
            select(SettlementEvent).where(SettlementEvent.bet_id == bet_id)
        )
        if existing_settlement is not None:
            if existing_settlement.result != result.value:
                raise SettlementConflict("bet was already settled with another result")
            return existing_settlement
        bet = await self._session.scalar(
            select(BetRecord).where(BetRecord.id == bet_id).with_for_update()
        )
        if bet is None:
            raise SettlementConflict("bet does not exist")
        if bet.status != BetStatus.PENDING:
            raise SettlementConflict("bet is not pending")
        payout = payout_for_result(result, bet.stake, bet.odds)
        if payout > 0:
            bankroll = await self._session.scalar(
                select(Bankroll).where(Bankroll.user_id == bet.user_id)
            )
            if bankroll is None:
                raise SettlementConflict("user has no bankroll")
            self._session.add(
                BankrollTransaction(
                    bankroll_id=bankroll.id,
                    transaction_type=(
                        BankrollTransactionType.WIN
                        if result == BetStatus.WON
                        else BankrollTransactionType.VOID
                    ),
                    amount=payout,
                    idempotency_key=f"settlement:{bet_id}",
                    reference_id=str(bet_id),
                )
            )
        bet.status = result
        settlement = SettlementEvent(
            bet_id=bet_id,
            result=result.value,
            settled_at=datetime.now(UTC),
            payout_amount=payout,
        )
        self._session.add(settlement)
        await self._session.commit()
        return settlement
