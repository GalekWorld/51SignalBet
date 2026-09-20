"""Deterministic user betting statistics."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class SettledBet:
    """Minimum immutable input needed for performance statistics."""

    placed_at: datetime
    status: str
    odds: Decimal
    stake: Decimal
    sport: str | None = None
    league: str | None = None
    market: str | None = None
    bookmaker: str | None = None
    edge: Decimal | None = None


@dataclass(frozen=True)
class BettingStatistics:
    """Explicitly defined performance metrics."""

    bets: int
    wins: int
    losses: int
    voids: int
    hit_rate: Decimal
    profit: Decimal
    roi: Decimal
    yield_value: Decimal
    average_odds: Decimal
    average_stake: Decimal
    average_edge: Decimal | None
    max_drawdown: Decimal
    winning_streak: int
    losing_streak: int


class StatisticsService:
    """Calculate statistics from settled bets without mutating source records."""

    def calculate(self, bets: list[SettledBet]) -> BettingStatistics:
        ordered = sorted(bets, key=lambda bet: bet.placed_at)
        wins = sum(bet.status == "won" for bet in ordered)
        losses = sum(bet.status == "lost" for bet in ordered)
        voids = sum(bet.status in {"void", "push"} for bet in ordered)
        profit_values = [self._profit(bet) for bet in ordered]
        profit = sum(profit_values, Decimal("0"))
        total_stake = sum(
            (bet.stake for bet in ordered if bet.status in {"won", "lost", "void", "push"}),
            Decimal("0"),
        )
        decisive_stake = sum(
            (bet.stake for bet in ordered if bet.status in {"won", "lost"}),
            Decimal("0"),
        )
        decisive = wins + losses
        edges = [bet.edge for bet in ordered if bet.edge is not None]
        return BettingStatistics(
            bets=len(ordered),
            wins=wins,
            losses=losses,
            voids=voids,
            hit_rate=Decimal(wins) / decisive if decisive else Decimal("0"),
            profit=profit,
            roi=profit / decisive_stake if decisive_stake else Decimal("0"),
            yield_value=profit / total_stake if total_stake else Decimal("0"),
            average_odds=self._average([bet.odds for bet in ordered]),
            average_stake=self._average([bet.stake for bet in ordered]),
            average_edge=self._average(edges) if edges else None,
            max_drawdown=self._max_drawdown(profit_values),
            winning_streak=self._max_streak(ordered, "won"),
            losing_streak=self._max_streak(ordered, "lost"),
        )

    def group_by(self, bets: list[SettledBet], dimension: str) -> dict[str, BettingStatistics]:
        """Return statistics grouped by one supported dimension."""

        if dimension not in {"sport", "league", "market", "bookmaker"}:
            raise ValueError("unsupported statistics dimension")
        groups: dict[str, list[SettledBet]] = {}
        for bet in bets:
            value = getattr(bet, dimension) or "unknown"
            groups.setdefault(value, []).append(bet)
        return {key: self.calculate(value) for key, value in groups.items()}

    @staticmethod
    def _profit(bet: SettledBet) -> Decimal:
        if bet.status == "won":
            return bet.stake * (bet.odds - Decimal("1"))
        if bet.status == "lost":
            return -bet.stake
        return Decimal("0")

    @staticmethod
    def _average(values: list[Decimal]) -> Decimal:
        return sum(values, Decimal("0")) / len(values) if values else Decimal("0")

    @staticmethod
    def _max_drawdown(profits: list[Decimal]) -> Decimal:
        peak = Decimal("0")
        balance = Decimal("0")
        maximum = Decimal("0")
        for profit in profits:
            balance += profit
            peak = max(peak, balance)
            maximum = max(maximum, peak - balance)
        return maximum

    @staticmethod
    def _max_streak(bets: list[SettledBet], status: str) -> int:
        current = maximum = 0
        for bet in bets:
            current = current + 1 if bet.status == status else 0
            maximum = max(maximum, current)
        return maximum
