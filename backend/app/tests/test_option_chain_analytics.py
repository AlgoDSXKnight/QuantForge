from datetime import date

import pytest

from app.pricing.option_chain import OptionChain
from app.pricing.option_chain_analytics import (
    OptionChainAnalytics,
    build_option_chain_analytics,
    calculate_atm_iv,
    calculate_call_put_iv_difference,
    calculate_expiration_iv,
    calculate_strike_iv,
    calculate_strike_skew,
)
from app.pricing.option_chain_iv import (
    OptionChainIVPoint,
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
        create_point("PUT", 1800.0, 0.27),
        create_point("CALL", 1900.0, 0.20),
        create_point("PUT", 1900.0, 0.22),
        create_point("CALL", 2000.0, 0.21),
        create_point("PUT", 2000.0, 0.23),
    ]


def create_chain() -> OptionChain:
    return OptionChain(
        underlying="INFY",
        timestamp=date(2026, 9, 1),
        underlying_price=1900.0,
        options=[],
    )


def test_calculate_atm_iv() -> None:
    call_iv, put_iv, atm_iv = calculate_atm_iv(
        points=create_points(),
        underlying_price=1900.0,
    )

    assert call_iv == pytest.approx(0.20)
    assert put_iv == pytest.approx(0.22)
    assert atm_iv == pytest.approx(0.21)


def test_calculate_atm_iv_uses_nearest_strike() -> None:
    points = [
        create_point("CALL", 1800.0, 0.30),
        create_point("CALL", 1950.0, 0.20),
        create_point("CALL", 2100.0, 0.25),
    ]

    call_iv, put_iv, atm_iv = calculate_atm_iv(
        points=points,
        underlying_price=1900.0,
    )

    assert call_iv == pytest.approx(0.20)
    assert put_iv is None
    assert atm_iv == pytest.approx(0.20)


def test_calculate_atm_iv_returns_none_when_no_points() -> None:
    result = calculate_atm_iv(
        points=[],
        underlying_price=1900.0,
    )

    assert result == (None, None, None)


def test_calculate_atm_iv_rejects_invalid_underlying_price() -> None:
    with pytest.raises(
        ValueError,
        match="Underlying price must be greater than zero",
    ):
        calculate_atm_iv(
            points=create_points(),
            underlying_price=0.0,
        )


def test_calculate_strike_iv() -> None:
    result = calculate_strike_iv(create_points())

    assert len(result) == 3

    assert result[0].strike == 1800.0
    assert result[0].call_iv == pytest.approx(0.24)
    assert result[0].put_iv == pytest.approx(0.27)

    assert result[1].strike == 1900.0
    assert result[1].call_iv == pytest.approx(0.20)
    assert result[1].put_iv == pytest.approx(0.22)

    assert result[2].strike == 2000.0
    assert result[2].call_iv == pytest.approx(0.21)
    assert result[2].put_iv == pytest.approx(0.23)


def test_calculate_strike_iv_handles_missing_option_type() -> None:
    points = [
        create_point("CALL", 1900.0, 0.20),
        create_point("CALL", 1900.0, 0.22),
        create_point("PUT", 2000.0, 0.25),
    ]

    result = calculate_strike_iv(points)

    assert len(result) == 2

    assert result[0].strike == 1900.0
    assert result[0].call_iv == pytest.approx(0.21)
    assert result[0].put_iv is None

    assert result[1].strike == 2000.0
    assert result[1].call_iv is None
    assert result[1].put_iv == pytest.approx(0.25)


def test_calculate_expiration_iv() -> None:
    first_expiration = date(2026, 12, 31)
    second_expiration = date(2027, 1, 30)

    points = [
        create_point(
            "CALL",
            1900.0,
            0.20,
            first_expiration,
        ),
        create_point(
            "PUT",
            1900.0,
            0.22,
            first_expiration,
        ),
        create_point(
            "CALL",
            1900.0,
            0.25,
            second_expiration,
        ),
        create_point(
            "PUT",
            1900.0,
            0.27,
            second_expiration,
        ),
    ]

    result = calculate_expiration_iv(points)

    assert len(result) == 2

    assert result[0].expiration == first_expiration
    assert result[0].call_iv == pytest.approx(0.20)
    assert result[0].put_iv == pytest.approx(0.22)

    assert result[1].expiration == second_expiration
    assert result[1].call_iv == pytest.approx(0.25)
    assert result[1].put_iv == pytest.approx(0.27)


def test_build_option_chain_analytics() -> None:
    analytics = build_option_chain_analytics(
        option_chain=create_chain(),
        iv_points=create_points(),
    )

    assert isinstance(analytics, OptionChainAnalytics)
    assert analytics.underlying == "INFY"
    assert analytics.timestamp == date(2026, 9, 1)
    assert analytics.underlying_price == 1900.0

    assert analytics.atm_call_iv == pytest.approx(0.20)
    assert analytics.atm_put_iv == pytest.approx(0.22)
    assert analytics.atm_iv == pytest.approx(0.21)

    assert len(analytics.strike_iv) == 3
    assert len(analytics.expiration_iv) == 1


def test_build_option_chain_analytics_rejects_empty_iv_points() -> None:
    with pytest.raises(
        ValueError,
        match="At least one IV point is required",
    ):
        build_option_chain_analytics(
            option_chain=create_chain(),
            iv_points=[],
        )


def test_build_option_chain_analytics_uses_valid_chain_price() -> None:
    chain = create_chain()

    analytics = build_option_chain_analytics(
        option_chain=chain,
        iv_points=create_points(),
    )

    assert analytics.underlying_price == pytest.approx(1900.0)

def test_calculate_call_put_iv_difference() -> None:
    analytics = build_option_chain_analytics(
        option_chain=create_chain(),
        iv_points=create_points(),
    )

    difference = calculate_call_put_iv_difference(
        analytics
    )

    assert difference == pytest.approx(-0.02)


def test_calculate_call_put_iv_difference_handles_missing_iv() -> None:
    analytics = OptionChainAnalytics(
        underlying="INFY",
        timestamp=date(2026, 9, 1),
        underlying_price=1900.0,
        atm_call_iv=0.20,
        atm_put_iv=None,
        atm_iv=0.20,
        strike_iv=[],
        expiration_iv=[],
    )

    assert calculate_call_put_iv_difference(analytics) is None


def test_calculate_strike_skew() -> None:
    analytics = build_option_chain_analytics(
        option_chain=create_chain(),
        iv_points=create_points(),
    )

    skew = calculate_strike_skew(
        analytics=analytics,
        lower_strike=1800.0,
        upper_strike=2000.0,
        option_type="CALL",
    )

    assert skew == pytest.approx(-0.03)


def test_calculate_put_strike_skew() -> None:
    analytics = build_option_chain_analytics(
        option_chain=create_chain(),
        iv_points=create_points(),
    )

    skew = calculate_strike_skew(
        analytics=analytics,
        lower_strike=1800.0,
        upper_strike=2000.0,
        option_type="PUT",
    )

    assert skew == pytest.approx(-0.04)


def test_calculate_strike_skew_normalizes_option_type() -> None:
    analytics = build_option_chain_analytics(
        option_chain=create_chain(),
        iv_points=create_points(),
    )

    skew = calculate_strike_skew(
        analytics=analytics,
        lower_strike=1800.0,
        upper_strike=2000.0,
        option_type="call",
    )

    assert skew == pytest.approx(-0.03)


def test_calculate_strike_skew_rejects_invalid_strike_order() -> None:
    analytics = build_option_chain_analytics(
        option_chain=create_chain(),
        iv_points=create_points(),
    )

    with pytest.raises(
        ValueError,
        match="Lower strike must be less than upper strike",
    ):
        calculate_strike_skew(
            analytics=analytics,
            lower_strike=2000.0,
            upper_strike=1800.0,
        )


def test_calculate_strike_skew_rejects_invalid_option_type() -> None:
    analytics = build_option_chain_analytics(
        option_chain=create_chain(),
        iv_points=create_points(),
    )

    with pytest.raises(
        ValueError,
        match="Option type must be CALL or PUT",
    ):
        calculate_strike_skew(
            analytics=analytics,
            lower_strike=1800.0,
            upper_strike=2000.0,
            option_type="XYZ",
        )


def test_calculate_strike_skew_rejects_missing_strike() -> None:
    analytics = build_option_chain_analytics(
        option_chain=create_chain(),
        iv_points=create_points(),
    )

    with pytest.raises(
        ValueError,
        match="Both strikes must exist in the analytics",
    ):
        calculate_strike_skew(
            analytics=analytics,
            lower_strike=1700.0,
            upper_strike=2000.0,
        )


def test_calculate_strike_skew_rejects_missing_option_type() -> None:
    points = [
        create_point("CALL", 1800.0, 0.24),
        create_point("CALL", 2000.0, 0.21),
    ]

    analytics = build_option_chain_analytics(
        option_chain=create_chain(),
        iv_points=points,
    )

    with pytest.raises(
        ValueError,
        match="Both strikes must contain the requested option type",
    ):
        calculate_strike_skew(
            analytics=analytics,
            lower_strike=1800.0,
            upper_strike=2000.0,
            option_type="PUT",
        )