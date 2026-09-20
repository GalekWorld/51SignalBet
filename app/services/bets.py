"""Virtual bet tracking use case."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BetRecord
from app.domain.bets import BetStatus


class InvalidBet(ValueError):
    """Bet data violates tracking invariants."""


class BetRecordService:
    """Record picks without settling them or executing real wagers."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: UUID,
        event_id: UUID,
        market: str,
        selection: str,
        odds: Decimal,
        stake: Decimal,
        units: Decimal | None,
        bookmaker_id: UUID | None,
        source: str,
        idempotency_key: str,
        placed_at: datetime | None = None,
    ) -> BetRecord:
        if odds <= Decimal("1"):
            raise InvalidBet("odds must be greater than 1")
        if stake <= Decimal("0"):
            raise InvalidBet("stake must be positive")
        existing = await self._session.scalar(
            select(BetRecord).where(
                BetRecord.user_id == user_id,
                BetRecord.idempotency_key == idempotency_key,
            )
        )
        if existing is not None:
            return existing
        bet = BetRecord(
            user_id=user_id,
            event_id=event_id,
            market=market,
            selection=selection,
            odds=odds,
            stake=stake,
            units=units,
            bookmaker_id=bookmaker_id,
            source=source,
            placed_at=(placed_at or datetime.now(UTC)).astimezone(UTC),
            status=BetStatus.PENDING,
            idempotency_key=idempotency_key,
        )
        self._session.add(bet)
        await self._session.commit()
        return bet
