"""Provider-neutral payment contracts; no payment provider is integrated yet."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class PaymentWebhook:
    """Validated event received from a payment provider adapter."""

    provider: str
    external_event_id: str
    user_reference: str
    plan: str
    amount: Decimal
    currency: str
    status: str


class PaymentProvider(Protocol):
    """Boundary for a future checkout/subscription provider."""

    async def create_checkout(self, *, user_reference: str, plan: str) -> str: ...

    def parse_webhook(self, payload: bytes, signature: str) -> PaymentWebhook: ...
