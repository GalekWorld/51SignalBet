from decimal import Decimal

from app.db.base import Base
from app.providers.payments import PaymentWebhook


def test_payment_webhook_contract_is_provider_neutral() -> None:
    webhook = PaymentWebhook("test", "evt-1", "user-1", "premium", Decimal("9.99"), "eur", "paid")

    assert webhook.currency == "eur"
    assert webhook.amount == Decimal("9.99")


def test_payment_events_are_deduplicated_by_provider_event() -> None:
    constraints = {
        constraint.name for constraint in Base.metadata.tables["payment_events"].constraints
    }

    assert "uq_payment_events_provider_external" in constraints
