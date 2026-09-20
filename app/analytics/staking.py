"""Conservative staking policies."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class StakingMethod(StrEnum):
    FLAT = "flat"
    FIXED_UNITS = "fixed_units"
    PERCENT_BANKROLL = "percent_bankroll"
    FRACTIONAL_KELLY = "fractional_kelly"


@dataclass(frozen=True)
class StakingPolicy:
    method: StakingMethod
    value: Decimal
    max_stake: Decimal | None = None


class StakingEngine:
    """Calculate a stake without martingale or loss-recovery behavior."""

    def stake(
        self,
        policy: StakingPolicy,
        *,
        bankroll: Decimal,
        odds: Decimal,
        probability: Decimal | None = None,
    ) -> Decimal:
        if bankroll < 0 or odds <= Decimal("1") or policy.value < 0:
            raise ValueError("bankroll, odds and policy values are invalid")
        if policy.method == StakingMethod.FLAT:
            result = policy.value
        elif policy.method == StakingMethod.FIXED_UNITS:
            result = policy.value
        elif policy.method == StakingMethod.PERCENT_BANKROLL:
            if policy.value > Decimal("1"):
                raise ValueError("percent bankroll must be a fraction")
            result = bankroll * policy.value
        else:
            if probability is None or not 0 <= probability <= 1:
                raise ValueError("probability is required for Kelly staking")
            if policy.value > 1:
                raise ValueError("fractional Kelly must be a fraction")
            edge = probability * odds - Decimal("1")
            full_kelly = edge / (odds - Decimal("1"))
            result = bankroll * max(Decimal("0"), full_kelly) * policy.value
        result = min(result, bankroll)
        if policy.max_stake is not None:
            if policy.max_stake < 0:
                raise ValueError("max_stake cannot be negative")
            result = min(result, policy.max_stake)
        return result
