"""Alert rule concepts."""

from enum import StrEnum


class AlertMetric(StrEnum):
    """Supported alert inputs."""

    ODDS = "odds"
    EXPECTED_VALUE = "expected_value"
    EDGE = "edge"
    MOVEMENT = "movement"


class AlertOperator(StrEnum):
    """Supported comparisons."""

    GREATER_EQUAL = "gte"
    LESS_EQUAL = "lte"
