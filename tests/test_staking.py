from decimal import Decimal

import pytest
from app.analytics.staking import StakingEngine, StakingMethod, StakingPolicy


def test_staking_supports_flat_percent_and_fractional_kelly() -> None:
    engine = StakingEngine()
    bankroll = Decimal("100")
    assert engine.stake(
        StakingPolicy(StakingMethod.FLAT, Decimal("5")), bankroll=bankroll, odds=Decimal("2")
    ) == Decimal("5")
    assert engine.stake(
        StakingPolicy(StakingMethod.PERCENT_BANKROLL, Decimal(".1")),
        bankroll=bankroll,
        odds=Decimal("2"),
    ) == Decimal("10")
    assert engine.stake(
        StakingPolicy(StakingMethod.FRACTIONAL_KELLY, Decimal(".5")),
        bankroll=bankroll,
        odds=Decimal("2"),
        probability=Decimal(".6"),
    ) == Decimal("10")


def test_staking_rejects_invalid_kelly_input() -> None:
    with pytest.raises(ValueError):
        StakingEngine().stake(
            StakingPolicy(StakingMethod.FRACTIONAL_KELLY, Decimal(".5")),
            bankroll=Decimal("100"),
            odds=Decimal("2"),
        )
