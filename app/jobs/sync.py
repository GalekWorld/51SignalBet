"""Jobs coordinating provider synchronization services."""

from dataclasses import dataclass

from app.jobs.runner import JobLock, RetryPolicy, run_job
from app.providers.contracts import OddsProvider, ProviderOddsSnapshot
from app.services.catalog_sync import CatalogSyncService
from app.services.event_ingestion import EventIngestionService, IngestionResult
from app.services.odds_snapshot_ingestion import OddsIngestionResult, OddsSnapshotIngestionService


@dataclass(frozen=True)
class SyncOddsResult:
    """Summary of one odds synchronization job."""

    events_processed: int
    snapshots: int
    skipped: int


class SyncEventsJob:
    """Synchronize provider events with a single distributed lock."""

    def __init__(self, service: EventIngestionService, lock: JobLock | None = None) -> None:
        self._service = service
        self._lock = lock

    async def run(
        self, *, sport: str | None = None, league: str | None = None
    ) -> IngestionResult | None:
        return await run_job(
            "sync-events",
            lambda: self._service.ingest_events(sport=sport, league=league),
            lock=self._lock,
            policy=RetryPolicy(max_attempts=3),
        )


class SyncSportsJob:
    """Synchronize the sport catalog under a distributed lock."""

    def __init__(self, service: CatalogSyncService, lock: JobLock | None = None) -> None:
        self._service = service
        self._lock = lock

    async def run(self) -> int | None:
        return await run_job(
            "sync-sports",
            self._service.sync_sports,
            lock=self._lock,
            policy=RetryPolicy(max_attempts=3),
        )


class SyncLeaguesJob:
    """Synchronize one sport's league catalog under a distributed lock."""

    def __init__(self, service: CatalogSyncService, lock: JobLock | None = None) -> None:
        self._service = service
        self._lock = lock

    async def run(self, sport: str) -> int | None:
        return await run_job(
            f"sync-leagues:{sport}",
            lambda: self._service.sync_leagues(sport),
            lock=self._lock,
            policy=RetryPolicy(max_attempts=3),
        )


class SyncOddsJob:
    """Fetch and persist current odds for a bounded set of event IDs."""

    def __init__(
        self,
        provider: OddsProvider,
        service: OddsSnapshotIngestionService,
        lock: JobLock | None = None,
    ) -> None:
        self._provider = provider
        self._service = service
        self._lock = lock

    async def run(self, provider_event_ids: list[str]) -> SyncOddsResult | None:
        async def operation() -> SyncOddsResult:
            snapshots: list[ProviderOddsSnapshot] = []
            for event_id in provider_event_ids:
                snapshots.append(await self._provider.get_odds(event_id))
            results: list[OddsIngestionResult] = []
            for snapshot in snapshots:
                results.append(await self._service.ingest(snapshot))
            return SyncOddsResult(
                events_processed=len(results),
                snapshots=sum(result.inserted for result in results),
                skipped=sum(result.skipped for result in results),
            )

        return await run_job(
            "sync-odds",
            operation,
            lock=self._lock,
            policy=RetryPolicy(max_attempts=3),
        )
