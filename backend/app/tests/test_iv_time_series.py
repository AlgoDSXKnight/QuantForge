from datetime import date

import pytest

from app.pricing.historical_iv import (
    HistoricalIVPoint,
)
from app.pricing.iv_time_series import (
    IVTimeSeriesPoint,
    build_iv_time_series,
    calculate_average_iv,
    calculate_iv_change,
    calculate_iv_change_percent,
    calculate_max_iv,
    calculate_min_iv,
)


def create_points() -> list[HistoricalIVPoint]:
    return [
        HistoricalIVPoint(
            underlying="INFY",
            timestamp=date(2026, 6, 1),
            option_type="CALL",
            strike=1900.0,
            expiration=date(2026, 12, 31),
            underlying_price=1900.0,
            option_price=100.0,
            implied_volatility=0.20,
        ),
        HistoricalIVPoint(
            underlying="INFY",
            timestamp=date(2026, 6, 2),
            option_type="CALL",
            strike=1900.0,
            expiration=date(2026, 12, 31),
            underlying_price=1920.0,
            option_price=110.0,
            implied_volatility=0.22,
        ),
        HistoricalIVPoint(
            underlying="INFY",
            timestamp=date(2026, 6, 3),
            option_type="CALL",
            strike=1900.0,
            expiration=date(2026, 12, 31),
            underlying_price=1950.0,
            option_price=130.0,
            implied_volatility=0.25,
        ),
    ]


def test_build_iv_time_series() -> None:
    points = create_points()

    result = build_iv_time_series(points)

    assert len(result) == 3

    assert isinstance(
        result[0],
        IVTimeSeriesPoint,
    )

    assert result[0].timestamp == date(
        2026,
        6,
        1,
    )

    assert result[0].implied_volatility == 0.20

    assert result[-1].implied_volatility == 0.25


def test_average_iv() -> None:
    points = create_points()

    result = calculate_average_iv(points)

    assert result == pytest.approx(
        0.22333333333333336,
    )


def test_min_iv() -> None:
    points = create_points()

    assert calculate_min_iv(points) == 0.20


def test_max_iv() -> None:
    points = create_points()

    assert calculate_max_iv(points) == 0.25


def test_iv_change() -> None:
    points = create_points()

    result = calculate_iv_change(points)

    assert result == pytest.approx(
        0.05,
    )


def test_iv_change_percent() -> None:
    points = create_points()

    result = calculate_iv_change_percent(points)

    assert result == pytest.approx(
        25.0,
    )


def test_single_point_change_is_zero() -> None:
    points = create_points()[:1]

    assert calculate_iv_change(points) == 0.0
    assert calculate_iv_change_percent(points) == 0.0


def test_requires_points() -> None:
    with pytest.raises(
        ValueError,
        match="At least one historical IV point",
    ):
        build_iv_time_series([])


def test_rejects_non_chronological_points() -> None:
    points = create_points()

    points = [
        points[1],
        points[0],
        points[2],
    ]

    with pytest.raises(
        ValueError,
        match="strictly chronological",
    ):
        build_iv_time_series(points)


def test_rejects_non_positive_iv() -> None:
    points = create_points()

    points[0] = HistoricalIVPoint(
        underlying="INFY",
        timestamp=date(2026, 6, 1),
        option_type="CALL",
        strike=1900.0,
        expiration=date(2026, 12, 31),
        underlying_price=1900.0,
        option_price=100.0,
        implied_volatility=0.0,
    )

    with pytest.raises(
        ValueError,
        match="Implied volatility",
    ):
        build_iv_time_series(points)