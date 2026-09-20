from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from app.analytics.clv import ClosingLineService, ClosingQuote


def test_clv_uses_last_available_quote_before_kickoff() -> None:
    start = datetime(2026, 9, 20, 15, tzinfo=UTC)
    pick_time = start - timedelta(hours=2)
    result = ClosingLineService().calculate(
        pick_odds=Decimal("2.20"),
        pick_timestamp=pick_time,
        event_start=start,
        quotes=[
            ClosingQuote("book", Decimal("2.10"), start - timedelta(hours=1)),
            ClosingQuote("book", Decimal("2.00"), start - timedelta(minutes=5)),
            ClosingQuote("book", Decimal("1.80"), start + timedelta(minutes=5)),
        ],
    )

    assert result.closing_odds == Decimal("2.00")
    assert result.clv == Decimal("0.0454545454545454545454545455")


def test_clv_ignores_suspended_and_other_bookmaker_quotes() -> None:
    start = datetime(2026, 9, 20, 15, tzinfo=UTC)
    with pytest.raises(ValueError):
        ClosingLineService().calculate(
            pick_odds=Decimal("2.00"),
            pick_timestamp=start - timedelta(hours=1),
            event_start=start,
            quotes=[
                ClosingQuote("other", Decimal("1.50"), start - timedelta(minutes=1)),
                ClosingQuote("book", Decimal("1.50"), start - timedelta(minutes=1), False),
            ],
            bookmaker="book",
        )
