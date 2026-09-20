from decimal import Decimal

from app.db.base import Base
from app.domain.bets import BetStatus
from app.services.bets import InvalidBet


def test_bet_statuses_cover_tracking_lifecycle() -> None:
    assert {status.value for status in BetStatus} == {
        "pending",
        "won",
        "lost",
        "void",
        "push",
        "cancelled",
    }


def test_bet_record_schema_is_historical() -> None:
    table = Base.metadata.tables["bet_records"]

    assert table.c.odds.type.scale == 4
    assert table.c.placed_at.type.timezone is True
    assert issubclass(InvalidBet, ValueError)
    assert Decimal("1.01") > Decimal("1")
