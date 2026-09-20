"""Alert evaluation and deduplicated trigger creation."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AlertEvent, AlertRule
from app.domain.alerts import AlertMetric, AlertOperator


@dataclass(frozen=True)
class AlertInput:
    """Metrics and dimensions evaluated against one opportunity or movement."""

    dedup_key: str
    odds: Decimal | None = None
    expected_value: Decimal | None = None
    edge: Decimal | None = None
    movement: Decimal | None = None
    dimensions: dict[str, str] | None = None


def matches(rule: AlertRule, alert_input: AlertInput) -> bool:
    """Evaluate metric, operator and optional dimensions without side effects."""

    values = {
        AlertMetric.ODDS: alert_input.odds,
        AlertMetric.EXPECTED_VALUE: alert_input.expected_value,
        AlertMetric.EDGE: alert_input.edge,
        AlertMetric.MOVEMENT: alert_input.movement,
    }
    value = values[rule.metric]
    if value is None:
        return False
    dimensions = alert_input.dimensions or {}
    if any(dimensions.get(key) != str(expected) for key, expected in rule.filters.items()):
        return False
    if rule.operator == AlertOperator.GREATER_EQUAL:
        return value >= rule.threshold
    return value <= rule.threshold


class AlertService:
    """Create one alert event per rule/dedup key and enforce cooldown."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def evaluate(self, rule: AlertRule, alert_input: AlertInput) -> AlertEvent | None:
        if not rule.enabled or not matches(rule, alert_input):
            return None
        existing = await self._session.scalar(
            select(AlertEvent)
            .where(AlertEvent.rule_id == rule.id)
            .where(AlertEvent.dedup_key == alert_input.dedup_key)
        )
        now = datetime.now(UTC)
        if existing is not None:
            return None
        recent = await self._session.scalar(
            select(AlertEvent)
            .where(AlertEvent.rule_id == rule.id)
            .where(AlertEvent.triggered_at >= now - timedelta(seconds=rule.cooldown_seconds))
            .order_by(AlertEvent.triggered_at.desc())
        )
        if recent is not None:
            return None
        statement = (
            pg_insert(AlertEvent)
            .values(
                rule_id=rule.id,
                dedup_key=alert_input.dedup_key,
                triggered_at=now,
                delivered=False,
            )
            .on_conflict_do_nothing(index_elements=[AlertEvent.rule_id, AlertEvent.dedup_key])
            .returning(AlertEvent.id)
        )
        event_id = await self._session.scalar(statement)
        await self._session.commit()
        if event_id is None:
            return None
        return await self._session.get(AlertEvent, event_id)
