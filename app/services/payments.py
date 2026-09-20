"""Payment webhook processing behind a provider-neutral boundary."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PaymentEvent
from app.providers.payments import PaymentWebhook


class PaymentService:
    """Persist webhook events once; entitlement mutation remains explicit."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_webhook(
        self,
        *,
        user_id: UUID,
        webhook: PaymentWebhook,
        payload: dict[str, object],
    ) -> PaymentEvent:
        existing = await self._session.scalar(
            select(PaymentEvent).where(
                PaymentEvent.provider == webhook.provider,
                PaymentEvent.external_event_id == webhook.external_event_id,
            )
        )
        if existing is not None:
            return existing
        event = PaymentEvent(
            user_id=user_id,
            provider=webhook.provider,
            external_event_id=webhook.external_event_id,
            plan=webhook.plan,
            amount=webhook.amount,
            currency=webhook.currency.upper(),
            status=webhook.status,
            payload=payload,
            received_at=datetime.now(UTC),
        )
        self._session.add(event)
        await self._session.commit()
        return event
