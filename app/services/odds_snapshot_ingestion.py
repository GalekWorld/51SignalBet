"""Append-only ingestion of normalized odds snapshots."""

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.text import normalize_name
from app.db.models import Bookmaker, Event, OddsSnapshot
from app.providers.contracts import ProviderOddsSnapshot


@dataclass(frozen=True)
class OddsIngestionResult:
    """Counters for one snapshot ingestion operation."""

    inserted: int
    skipped: int


class OddsSnapshotIngestionService:
    """Store every provider observation without mutating historical rows."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def ingest(
        self,
        snapshot: ProviderOddsSnapshot,
        *,
        provider: str = "odds_api",
        received_at: datetime | None = None,
    ) -> OddsIngestionResult:
        """Append valid lines for an internal event and commit atomically."""

        event = await self._session.scalar(
            select(Event).where(
                Event.provider == provider,
                Event.provider_event_id == snapshot.provider_event_id,
            )
        )
        if event is None:
            return OddsIngestionResult(inserted=0, skipped=len(snapshot.lines))

        provider_ts = snapshot.as_of or datetime.now(UTC)
        received_ts = (received_at or datetime.now(UTC)).astimezone(UTC)
        inserted = 0
        skipped = 0
        for line in snapshot.lines:
            if not line.market_key or line.odds is None:
                skipped += 1
                continue
            bookmaker = await self._get_or_create_bookmaker(line.bookmaker)
            self._session.add(
                OddsSnapshot(
                    event_id=event.id,
                    bookmaker_id=bookmaker.id,
                    provider=provider,
                    provider_line_id=line.id,
                    market_key=line.market_key,
                    selection=line.selection,
                    line=line.line,
                    odds=line.odds,
                    provider_ts=provider_ts,
                    received_ts=received_ts,
                    is_available=line.is_available,
                )
            )
            inserted += 1
        await self._session.flush()
        await self._session.commit()
        return OddsIngestionResult(inserted=inserted, skipped=skipped)

    async def _get_or_create_bookmaker(self, value: str) -> Bookmaker:
        code = normalize_name(value).replace(" ", "_")
        bookmaker = await self._session.scalar(select(Bookmaker).where(Bookmaker.code == code))
        if bookmaker is None:
            bookmaker = Bookmaker(code=code, name=value.strip())
            self._session.add(bookmaker)
            await self._session.flush()
        return bookmaker
