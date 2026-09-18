from datetime import date

import pytest

from app.pricing.option_chain_iv import OptionChainIVPoint
from app.pricing.option_chain_surface import (
    convert_iv_points_to_surface_points,
)
from app.pricing.volatility_surface_analytics import (
    ExpirationStatistics,
    SmileStatistics,
    SurfaceDataQuality,
    SurfaceStatistics,
    TermStructureStatistics,
    analyze_surface_data_quality,
    calculate_expiration_statistics,
    calculate_smile_statistics,
    calculate_surface_statistics,
    calculate_term_structure_statistics,
)


def create_point(
    option_type: str,
    strike: float,
    volatility: float,
    expiration: date = date(2026, 12, 31),
) -> OptionChainIVPoint:
    return OptionChainIVPoint(
        underlying="INFY",
        timestamp=date(2026, 9, 1),
        option_type=option_type,
        strike=strike,
        expiration=expiration,
        option_price=100.0,
        underlying_price=1900.0,
        implied_volatility=volatility,
    )


def create_surface_points():
    iv_points = [
        create_point("CALL", 1800.0, 0.24),
        create_point("PUT", 1800.0, 0.27),
        create_point("CALL", 1900.0, 0.20),
        create_point("PUT", 1900.0, 0.22),
        create_point("CALL", 2000.0, 0.21),
        create_point("PUT", 2000.0, 0.23),
    ]

    return convert_iv_points_to_surface_points(iv_points)


def test_calculate_surface_statistics() -> None:
    result = calculate_surface_statistics(
        create_surface_points()
    )

    assert isinstance(result, SurfaceStatistics)
    assert result.point_count == 6
    assert result.average_iv == pytest.approx(
        (0.24 + 0.27 + 0.20 + 0.22 + 0.21 + 0.23) / 6
    )
    assert result.minimum_iv == pytest.approx(0.20)
    assert result.maximum_iv == pytest.approx(0.27)
    assert result.iv_range == pytest.approx(0.07)


def test_calculate_surface_statistics_rejects_empty() -> None:
    with pytest.raises(
        ValueError,
        match="At least one volatility point is required",
    ):
        calculate_surface_statistics([])


def test_calculate_expiration_statistics() -> None:
    result = calculate_expiration_statistics(
        create_surface_points()
    )

    assert len(result) == 1
    assert isinstance(result[0], ExpirationStatistics)
    assert result[0].point_count == 6
    assert result[0].minimum_iv == pytest.approx(0.20)
    assert result[0].maximum_iv == pytest.approx(0.27)
    assert result[0].call_iv == pytest.approx(
        (0.24 + 0.20 + 0.21) / 3
    )
    assert result[0].put_iv == pytest.approx(
        (0.27 + 0.22 + 0.23) / 3
    )


def test_calculate_expiration_statistics_rejects_empty() -> None:
    with pytest.raises(
        ValueError,
        match="At least one volatility point is required",
    ):
        calculate_expiration_statistics([])


def test_calculate_term_structure_statistics() -> None:
    points = [
        create_point(
            "CALL",
            1900.0,
            0.20,
            date(2026, 12, 31),
        ),
        create_point(
            "CALL",
            1900.0,
            0.24,
            date(2027, 1, 30),
        ),
    ]

    surface = convert_iv_points_to_surface_points(points)

    result = calculate_term_structure_statistics(
        surface,
        1900.0,
    )

    assert isinstance(result, TermStructureStatistics)
    assert result.first_iv == pytest.approx(0.20)
    assert result.last_iv == pytest.approx(0.24)
    assert result.absolute_change == pytest.approx(0.04)
    assert result.relative_change == pytest.approx(0.20)
    assert result.slope > 0


def test_calculate_term_structure_rejects_invalid_strike() -> None:
    with pytest.raises(
        ValueError,
        match="Strike price must be greater than zero",
    ):
        calculate_term_structure_statistics(
            create_surface_points(),
            0.0,
        )


def test_calculate_term_structure_requires_two_expirations() -> None:
    with pytest.raises(
        ValueError,
        match="At least two expirations are required",
    ):
        calculate_term_structure_statistics(
            create_surface_points(),
            1900.0,
        )


def test_calculate_smile_statistics() -> None:
    result = calculate_smile_statistics(
        create_surface_points(),
        create_surface_points()[0].time_to_expiry,
    )

    assert isinstance(result, SmileStatistics)
    assert result.atm_strike == pytest.approx(1900.0)
    assert result.atm_iv == pytest.approx(
        (0.20 + 0.22) / 2
    )
    assert result.lower_strike == pytest.approx(1800.0)
    assert result.upper_strike == pytest.approx(2000.0)
    assert result.lower_iv == pytest.approx(
        (0.24 + 0.27) / 2
    )
    assert result.upper_iv == pytest.approx(
        (0.21 + 0.23) / 2
    )
    assert result.skew == pytest.approx(
        ((0.21 + 0.23) / 2 - (0.24 + 0.27) / 2)
        / 200.0
    )


def test_calculate_smile_rejects_invalid_expiry() -> None:
    with pytest.raises(
        ValueError,
        match="Time to expiry must be greater than zero",
    ):
        calculate_smile_statistics(
            create_surface_points(),
            0.0,
        )


def test_calculate_smile_rejects_missing_expiry() -> None:
    with pytest.raises(
        ValueError,
        match="No volatility points found",
    ):
        calculate_smile_statistics(
            create_surface_points(),
            10.0,
        )


def test_surface_data_quality() -> None:
    result = analyze_surface_data_quality(
        create_surface_points()
    )

    assert isinstance(result, SurfaceDataQuality)
    assert result.point_count == 6
    assert result.expiration_count == 1
    assert result.strike_count == 3
    assert result.duplicate_count == 0
    assert result.duplicate_keys == []


def test_surface_data_quality_detects_duplicates() -> None:
    points = create_surface_points()

    points.append(points[0])

    result = analyze_surface_data_quality(points)

    assert result.duplicate_count == 1
    assert result.duplicate_keys == [
        (1800.0, points[0].time_to_expiry, "CALL")
    ]


def test_surface_data_quality_rejects_empty() -> None:
    with pytest.raises(
        ValueError,
        match="At least one volatility point is required",
    ):
        analyze_surface_data_quality([])