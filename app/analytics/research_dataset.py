"""Reproducible historical research dataset construction."""

import csv
import io
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class HistoricalOddsRecord:
    """Normalized source row used for research exports."""

    event_id: str
    sport: str
    league: str | None
    market: str
    selection: str
    bookmaker: str
    odds: Decimal
    provider_timestamp: datetime
    event_start: datetime
    result: str | None = None


@dataclass(frozen=True)
class ResearchDataset:
    """Immutable dataset metadata and rows."""

    dataset_version: str
    generated_at: datetime
    rows: tuple[HistoricalOddsRecord, ...]

    def to_csv(self) -> str:
        """Serialize with explicit columns and decimal string values."""

        output = io.StringIO()
        fields = [
            "event_id",
            "sport",
            "league",
            "market",
            "selection",
            "bookmaker",
            "odds",
            "provider_timestamp",
            "event_start",
            "result",
        ]
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row in self.rows:
            writer.writerow(
                {
                    "event_id": row.event_id,
                    "sport": row.sport,
                    "league": row.league or "",
                    "market": row.market,
                    "selection": row.selection,
                    "bookmaker": row.bookmaker,
                    "odds": str(row.odds),
                    "provider_timestamp": row.provider_timestamp.isoformat(),
                    "event_start": row.event_start.isoformat(),
                    "result": row.result or "",
                }
            )
        return output.getvalue()


class ResearchDatasetBuilder:
    """Build point-in-time-safe datasets without future observations."""

    def build(
        self,
        records: list[HistoricalOddsRecord],
        *,
        dataset_version: str,
        generated_at: datetime,
        from_timestamp: datetime | None = None,
        to_timestamp: datetime | None = None,
        require_result: bool = False,
    ) -> ResearchDataset:
        filtered = [
            record
            for record in records
            if (from_timestamp is None or record.provider_timestamp >= from_timestamp)
            and (to_timestamp is None or record.provider_timestamp <= to_timestamp)
            and record.provider_timestamp <= generated_at
            and (not require_result or record.result is not None)
        ]
        filtered.sort(
            key=lambda record: (record.provider_timestamp, record.event_id, record.selection)
        )
        return ResearchDataset(
            dataset_version=dataset_version, generated_at=generated_at, rows=tuple(filtered)
        )
