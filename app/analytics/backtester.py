"""Small strict-temporal backtesting engine."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class BacktestBet:
    """Historical bet candidate with explicit information availability time."""

    event_id: str
    placed_at: datetime
    information_at: datetime
    result_at: datetime
    odds: Decimal
    stake: Decimal
    outcome: str


@dataclass(frozen=True)
class BacktestResult:
    """Bankroll simulation summary."""

    initial_bankroll: Decimal
    final_bankroll: Decimal
    profit: Decimal
    executed: int
    skipped_insufficient_bankroll: int
    roi: Decimal
    yield_value: Decimal
    max_drawdown: Decimal


class BacktestEngine:
    """Run a deterministic no-lookahead bankroll simulation."""

    def run(self, bets: list[BacktestBet], *, initial_bankroll: Decimal) -> BacktestResult:
        if initial_bankroll < 0:
            raise ValueError("initial_bankroll cannot be negative")
        ordered = sorted(bets, key=lambda bet: (bet.placed_at, bet.event_id))
        bankroll = initial_bankroll
        executed = skipped = 0
        total_stake = Decimal("0")
        peak = bankroll
        max_drawdown = Decimal("0")
        for bet in ordered:
            if bet.information_at > bet.placed_at or bet.result_at <= bet.placed_at:
                raise ValueError("backtest input contains lookahead or invalid temporal ordering")
            if bet.odds <= Decimal("1") or bet.stake <= Decimal("0"):
                raise ValueError("bet odds and stake must be positive")
            if bet.stake > bankroll:
                skipped += 1
                continue
            bankroll -= bet.stake
            if bet.outcome == "won":
                bankroll += bet.stake * bet.odds
            elif bet.outcome in {"void", "push"}:
                bankroll += bet.stake
            elif bet.outcome != "lost":
                raise ValueError(f"unsupported outcome: {bet.outcome}")
            total_stake += bet.stake
            executed += 1
            peak = max(peak, bankroll)
            max_drawdown = max(max_drawdown, peak - bankroll)
        profit = bankroll - initial_bankroll
        return BacktestResult(
            initial_bankroll=initial_bankroll,
            final_bankroll=bankroll,
            profit=profit,
            executed=executed,
            skipped_insufficient_bankroll=skipped,
            roi=profit / initial_bankroll if initial_bankroll else Decimal("0"),
            yield_value=profit / total_stake if total_stake else Decimal("0"),
            max_drawdown=max_drawdown,
        )
