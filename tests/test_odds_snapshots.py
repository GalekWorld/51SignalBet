from datetime import UTC, datetime
from decimal import Decimal

from app.db.base import Base
from app.db.models import OddsSnapshot
from app.providers.contracts import ProviderOddsLine, ProviderOddsSnapshot


def test_odds_snapshot_table_is_append_only_and_indexed() -> None:
    table = Base.metadata.tables["odds_snapshots"]

    assert table.c.provider_ts.type.timezone is True
    assert table.c.received_ts.type.timezone is True
    assert table.c.odds.type.scale == 4
    assert any(
        index.name == "ix_odds_snapshots_event_market_provider_ts" for index in table.indexes
    )
    assert OddsSnapshot.__table__.primary_key is not None


def test_provider_snapshot_preserves_decimal_values_and_utc_time() -> None:
    snapshot = ProviderOddsSnapshot(
        provider_event_id="evt-1",
        as_of=datetime(2026, 9, 20, 12, tzinfo=UTC),
        lines=(
            ProviderOddsLine(
                id="line-1",
                provider_event_id="evt-1",
                bookmaker="pinnacle",
                market_key="moneyline",
                selection="Home",
                odds=Decimal("2.10"),
            ),
        ),
        resume="0-1",
    )

    assert snapshot.lines[0].odds == Decimal("2.10")
    assert snapshot.as_of is not None and snapshot.as_of.tzinfo == UTC
