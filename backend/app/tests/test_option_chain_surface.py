from datetime import date

import pytest

from app.pricing.option_chain import OptionChain
from app.pricing.option_chain_iv import OptionChainIVPoint
from app.pricing.option_chain_surface import (
    build_smile_from_option_chain,
    build_surface_from_option_chain,
    build_term_structure_from_option_chain,
    calculate_chain_skew,
    convert_iv_points_to_surface_points,
)
from app.pricing.volatility_surface import (
    VolatilityPoint,
    VolatilitySmile,
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


def create_points() -> list[OptionChainIVPoint]:
    return [
        create_point("CALL", 1800.0, 0.24),
        create_point("CALL", 1900.0, 0.20),
        create_point("CALL", 2000.0, 0.21),
        create_point("PUT", 1800.0, 0.27),
        create_point("PUT", 1900.0, 0.22),
        create_point("PUT", 2000.0, 0.23),
    ]


def create_chain() -> OptionChain:
    return OptionChain(
        underlying="INFY",
        timestamp=date(2026, 9, 1),
        underlying_price=1900.0,
        options=[],
    )


def test_convert_iv_points_to_surface_points() -> None:
    result = convert_iv_points_to_surface_points(
        create_points()
    )

    assert len(result) == 6
    assert isinstance(result[0], VolatilityPoint)

    assert result[0].strike_price == pytest.approx(1800.0)
    assert result[0].time_to_expiry == pytest.approx(
        (date(2026, 12, 31) - date(2026, 9, 1)).days / 365.0
    )
    assert result[0].implied_volatility == pytest.approx(0.24)
    assert result[0].option_type == "CALL"


def test_convert_iv_points_rejects_empty_input() -> None:
    with pytest.raises(
        ValueError,
        match="At least one IV point is required",
    ):
        convert_iv_points_to_surface_points([])


def test_build_surface_from_option_chain() -> None:
    result = build_surface_from_option_chain(
        option_chain=create_chain(),
        iv_points=create_points(),
    )

    assert len(result) == 6
    assert all(
        isinstance(point, VolatilityPoint)
        for point in result
    )


def test_build_surface_rejects_empty_iv_points() -> None:
    with pytest.raises(
        ValueError,
        match="At least one IV point is required",
    ):
        build_surface_from_option_chain(
            option_chain=create_chain(),
            iv_points=[],
        )


def test_build_surface_accepts_valid_underlying_price() -> None:
    result = build_surface_from_option_chain(
        option_chain=create_chain(),
        iv_points=create_points(),
    )

    assert len(result) == 6


def test_build_surface_rejects_mismatched_underlying() -> None:
    points = [
        OptionChainIVPoint(
            underlying="TCS",
            timestamp=date(2026, 9, 1),
            option_type="CALL",
            strike=1900.0,
            expiration=date(2026, 12, 31),
            option_price=100.0,
            underlying_price=1900.0,
            implied_volatility=0.20,
        )
    ]

    with pytest.raises(
        ValueError,
        match="underlying does not match",
    ):
        build_surface_from_option_chain(
            option_chain=create_chain(),
            iv_points=points,
        )


def test_build_surface_rejects_mismatched_timestamp() -> None:
    points = [
        OptionChainIVPoint(
            underlying="INFY",
            timestamp=date(2026, 9, 2),
            option_type="CALL",
            strike=1900.0,
            expiration=date(2026, 12, 31),
            option_price=100.0,
            underlying_price=1900.0,
            implied_volatility=0.20,
        )
    ]

    with pytest.raises(
        ValueError,
        match="timestamp does not match",
    ):
        build_surface_from_option_chain(
            option_chain=create_chain(),
            iv_points=points,
        )


def test_build_smile_from_option_chain() -> None:
    result = build_smile_from_option_chain(
        option_chain=create_chain(),
        iv_points=create_points(),
        expiration=date(2026, 12, 31),
    )

    assert isinstance(result, VolatilitySmile)
    assert len(result.points) == 6

    assert result.points[0].strike_price == pytest.approx(
        1800.0
    )


def test_build_term_structure_from_option_chain() -> None:
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

    result = build_term_structure_from_option_chain(
        option_chain=create_chain(),
        iv_points=points,
        strike=1900.0,
    )

    assert len(result) == 2
    assert result[0].implied_volatility == pytest.approx(0.20)
    assert result[1].implied_volatility == pytest.approx(0.24)
    assert result[0].time_to_expiry < result[1].time_to_expiry


def test_calculate_chain_skew() -> None:
    result = calculate_chain_skew(
        option_chain=create_chain(),
        iv_points=create_points(),
        expiration=date(2026, 12, 31),
        lower_strike=1800.0,
        upper_strike=2000.0,
    )

    expected = (
        (0.21 - 0.24)
        / (2000.0 - 1800.0)
    )

    assert result == pytest.approx(expected)