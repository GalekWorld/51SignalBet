from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.analytics.research_dataset import HistoricalOddsRecord, ResearchDatasetBuilder


def test_dataset_excludes_future_observations_and_can_require_results() -> None:
    generated = datetime(2026, 9, 20, 12, tzinfo=UTC)
    records = [
        HistoricalOddsRecord(
            "evt-1",
            "football",
            "EPL",
            "winner",
            "home",
            "book",
            Decimal("2.1"),
            generated - timedelta(hours=1),
            generated,
            "won",
        ),
        HistoricalOddsRecord(
            "evt-2",
            "football",
            "EPL",
            "winner",
            "away",
            "book",
            Decimal("2.1"),
            generated + timedelta(hours=1),
            generated,
            None,
        ),
    ]

    dataset = ResearchDatasetBuilder().build(
        records, dataset_version="v1", generated_at=generated, require_result=True
    )

    assert len(dataset.rows) == 1
    assert "evt-1" in dataset.to_csv()
    assert "evt-2" not in dataset.to_csv()
