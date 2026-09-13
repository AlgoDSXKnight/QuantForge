from datetime import date

import pytest

from app.pricing.black_scholes import (
    black_scholes_call,
)
from app.pricing.historical_iv import (
    HistoricalIVPoint,
    calculate_historical_iv,
)
from app.pricing.option_market_data import (
    OptionMarketData,
)


def create_market_data(
    option_price: float,
) -> OptionMarketData:
    return OptionMarketData(
        underlying="INFY",
        timestamp=date(2026, 6, 1),
        option_type="CALL",
        strike=1900.0,
        expiration=date(2026, 12, 31),
        bid=option_price - 1.0,
        ask=option_price + 1.0,
        last_price=option_price,
        underlying_price=1900.0,
    )


def test_calculate_historical_iv() -> None:
    spot = 1900.0
    strike = 1900.0
    time_to_expiry = (
        date(2026, 12, 31)
        - date(2026, 6, 1)
    ).days / 365.0

    market_price = black_scholes_call(
        spot_price=spot,
        strike_price=strike,
        time_to_expiry=time_to_expiry,
        risk_free_rate=0.05,
        volatility=0.20,
    )

    market_data = create_market_data(
        option_price=market_price,
    )

    result = calculate_historical_iv(
        market_data=market_data,
        risk_free_rate=0.05,
    )

    assert isinstance(
        result,
        HistoricalIVPoint,
    )

    assert result.underlying == "INFY"
    assert result.option_type == "CALL"
    assert result.strike == 1900.0

    assert result.implied_volatility == pytest.approx(
        0.20,
        abs=1e-5,
    )


def test_historical_iv_uses_mid_price() -> None:
    market_data = create_market_data(
        option_price=100.0,
    )

    result = calculate_historical_iv(
        market_data=market_data,
        risk_free_rate=0.05,
    )

    assert result.option_price == pytest.approx(
        100.0,
    )


def test_historical_iv_changes_with_option_price() -> None:
    low_price_data = create_market_data(
        option_price=100.0,
    )

    high_price_data = create_market_data(
        option_price=150.0,
    )

    low_iv = calculate_historical_iv(
        market_data=low_price_data,
        risk_free_rate=0.05,
    )

    high_iv = calculate_historical_iv(
        market_data=high_price_data,
        risk_free_rate=0.05,
    )

    assert (
        high_iv.implied_volatility
        > low_iv.implied_volatility
    )


def test_historical_iv_requires_valid_risk_free_rate() -> None:
    market_data = create_market_data(
        option_price=100.0,
    )

    with pytest.raises(
        ValueError,
        match="Risk-free rate",
    ):
        calculate_historical_iv(
            market_data=market_data,
            risk_free_rate=-1.0,
        )


def test_historical_iv_returns_metadata() -> None:
    market_data = create_market_data(
        option_price=100.0,
    )

    result = calculate_historical_iv(
        market_data=market_data,
        risk_free_rate=0.05,
    )

    assert result.timestamp == date(
        2026,
        6,
        1,
    )

    assert result.expiration == date(
        2026,
        12,
        31,
    )

    assert result.underlying_price == 1900.0