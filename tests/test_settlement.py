from decimal import Decimal

from app.db.base import Base
from app.domain.bets import BetStatus
from app.services.settlement import SettlementConflict, payout_for_result


def test_payouts_are_deterministic() -> None:
    assert payout_for_result(BetStatus.WON, Decimal("10"), Decimal("2.10")) == Decimal("21.0")
    assert payout_for_result(BetStatus.VOID, Decimal("10"), Decimal("2.10")) == Decimal("10")
    assert payout_for_result(BetStatus.PUSH, Decimal("10"), Decimal("2.10")) == Decimal("10")
    assert payout_for_result(BetStatus.LOST, Decimal("10"), Decimal("2.10")) == Decimal("0")


def test_settlement_table_is_unique_per_bet() -> None:
    constraints = {
        constraint.name for constraint in Base.metadata.tables["settlement_events"].constraints
    }
    assert "uq_settlement_events_bet_id" in constraints
    assert issubclass(SettlementConflict, ValueError)
