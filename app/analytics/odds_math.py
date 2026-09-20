"""Decimal-based odds and probability calculations.

Definitions used here:

* implied probability: ``1 / decimal_odds``;
* overround: sum of raw implied probabilities minus one;
* proportional de-vig probability: raw probability divided by the market sum;
* edge: model probability minus raw implied probability;
* expected value per unit staked: ``p * (odds - 1) - (1 - p)``.
"""

from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from typing import TypeVar


class OddsMathError(ValueError):
    """Base error for invalid mathematical inputs."""


class InvalidOdds(OddsMathError):
    """Odds are not valid decimal odds."""


class InvalidProbability(OddsMathError):
    """A probability is outside the closed interval [0, 1]."""


class InsufficientOutcomes(OddsMathError):
    """A market needs at least two outcomes for margin calculations."""


Key = TypeVar("Key", str, int)
Number = Decimal | int | str


def _decimal(value: Number) -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise OddsMathError("value must be numeric") from exc
    if not result.is_finite():
        raise OddsMathError("value must be finite")
    return result


def _probability(value: Number, *, allow_zero: bool = True) -> Decimal:
    result = _decimal(value)
    lower = Decimal("0") if allow_zero else Decimal("0")
    if result < lower or result > Decimal("1"):
        raise InvalidProbability("probability must be between 0 and 1")
    return result


def _odds(value: Number) -> Decimal:
    result = _decimal(value)
    if result <= Decimal("1"):
        raise InvalidOdds("decimal odds must be greater than 1")
    return result


def implied_probability(decimal_odds: Number) -> Decimal:
    """Convert decimal odds to raw implied probability."""

    return Decimal("1") / _odds(decimal_odds)


def raw_implied_probabilities(odds: Mapping[Key, Number]) -> dict[Key, Decimal]:  # noqa: UP047
    """Convert every market outcome to a raw implied probability."""

    if len(odds) < 2:
        raise InsufficientOutcomes("at least two outcomes are required")
    return {key: implied_probability(value) for key, value in odds.items()}


def overround(odds: Mapping[Key, Number]) -> Decimal:  # noqa: UP047
    """Return the bookmaker margin as a decimal fraction."""

    return sum(raw_implied_probabilities(odds).values(), Decimal("0")) - Decimal("1")


def de_vig(odds: Mapping[Key, Number]) -> dict[Key, Decimal]:  # noqa: UP047
    """Remove proportional bookmaker margin from a complete market."""

    raw = raw_implied_probabilities(odds)
    total = sum(raw.values(), Decimal("0"))
    if total <= Decimal("0"):
        raise InsufficientOutcomes("market probability sum must be positive")
    normalized = {key: probability / total for key, probability in raw.items()}
    # Keep the invariant exact at the active Decimal precision.
    last_key = next(reversed(normalized))
    normalized[last_key] = Decimal("1") - sum(
        value for key, value in normalized.items() if key != last_key
    )
    return normalized


def fair_odds(probability: Number) -> Decimal:
    """Convert a non-zero fair probability to decimal fair odds."""

    value = _probability(probability, allow_zero=False)
    if value == Decimal("0"):
        raise InvalidProbability("fair odds cannot be calculated for zero probability")
    return Decimal("1") / value


def fair_odds_for_market(odds: Mapping[Key, Number]) -> dict[Key, Decimal]:  # noqa: UP047
    """Return proportional de-vig fair odds for every market outcome."""

    return {key: fair_odds(probability) for key, probability in de_vig(odds).items()}


def edge(model_probability: Number, offered_odds: Number) -> Decimal:
    """Return model probability advantage over the offered raw probability."""

    probability = _probability(model_probability)
    return probability - implied_probability(offered_odds)


def expected_value(model_probability: Number, offered_odds: Number) -> Decimal:
    """Return expected profit per unit stake, as a decimal fraction."""

    probability = _probability(model_probability)
    odds = _odds(offered_odds)
    return probability * (odds - Decimal("1")) - (Decimal("1") - probability)
