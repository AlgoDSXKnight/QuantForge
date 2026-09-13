from dataclasses import dataclass
from datetime import date
from typing import Sequence

from app.pricing.historical_iv import (
    HistoricalIVPoint,
)


@dataclass(frozen=True)
class IVTimeSeriesPoint:
    timestamp: date
    implied_volatility: float


def _validate_points(
    points: Sequence[HistoricalIVPoint],
) -> None:
    if not points:
        raise ValueError(
            "At least one historical IV point is required."
        )

    previous_timestamp: date | None = None

    for point in points:
        if point.implied_volatility <= 0:
            raise ValueError(
                "Implied volatility must be greater than zero."
            )

        if (
            previous_timestamp is not None
            and point.timestamp <= previous_timestamp
        ):
            raise ValueError(
                "IV points must be strictly chronological."
            )

        previous_timestamp = point.timestamp


def build_iv_time_series(
    points: Sequence[HistoricalIVPoint],
) -> list[IVTimeSeriesPoint]:
    """
    Convert historical IV observations into a
    chronological IV time series.
    """

    _validate_points(points)

    return [
        IVTimeSeriesPoint(
            timestamp=point.timestamp,
            implied_volatility=point.implied_volatility,
        )
        for point in points
    ]


def calculate_average_iv(
    points: Sequence[HistoricalIVPoint],
) -> float:
    """
    Calculate the arithmetic mean implied volatility.
    """

    _validate_points(points)

    return sum(
        point.implied_volatility
        for point in points
    ) / len(points)


def calculate_min_iv(
    points: Sequence[HistoricalIVPoint],
) -> float:
    """
    Return the minimum observed implied volatility.
    """

    _validate_points(points)

    return min(
        point.implied_volatility
        for point in points
    )


def calculate_max_iv(
    points: Sequence[HistoricalIVPoint],
) -> float:
    """
    Return the maximum observed implied volatility.
    """

    _validate_points(points)

    return max(
        point.implied_volatility
        for point in points
    )


def calculate_iv_change(
    points: Sequence[HistoricalIVPoint],
) -> float:
    """
    Calculate the absolute change in IV from
    the first observation to the last observation.
    """

    _validate_points(points)

    if len(points) < 2:
        return 0.0

    return (
        points[-1].implied_volatility
        - points[0].implied_volatility
    )


def calculate_iv_change_percent(
    points: Sequence[HistoricalIVPoint],
) -> float:
    """
    Calculate the percentage change in IV from
    the first observation to the last observation.
    """

    _validate_points(points)

    if len(points) < 2:
        return 0.0

    initial_iv = points[0].implied_volatility

    return (
        (
            points[-1].implied_volatility
            - initial_iv
        )
        / initial_iv
    ) * 100.0