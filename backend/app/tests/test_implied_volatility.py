import pytest

from app.pricing.black_scholes import (
    black_scholes_call,
    black_scholes_put,
)
from app.pricing.implied_volatility import implied_volatility


SPOT = 100.0
STRIKE = 100.0
TIME = 1.0
RATE = 0.05
VOLATILITY = 0.20


def test_call_implied_volatility() -> None:
    market_price = black_scholes_call(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    )

    result = implied_volatility(
        spot_price=SPOT,
        strike_price=STRIKE,
        time_to_expiry=TIME,
        risk_free_rate=RATE,
        option_price=market_price,
        option_type="CALL",
    )

    assert result == pytest.approx(
        VOLATILITY,
        abs=1e-6,
    )


def test_put_implied_volatility() -> None:
    market_price = black_scholes_put(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    )

    result = implied_volatility(
        spot_price=SPOT,
        strike_price=STRIKE,
        time_to_expiry=TIME,
        risk_free_rate=RATE,
        option_price=market_price,
        option_type="PUT",
    )

    assert result == pytest.approx(
        VOLATILITY,
        abs=1e-6,
    )


@pytest.mark.parametrize(
    "option_type",
    ["CALL", "PUT"],
)
def test_implied_volatility_different_volatility(
    option_type: str,
) -> None:
    volatility = 0.35

    if option_type == "CALL":
        market_price = black_scholes_call(
            SPOT,
            STRIKE,
            TIME,
            RATE,
            volatility,
        )
    else:
        market_price = black_scholes_put(
            SPOT,
            STRIKE,
            TIME,
            RATE,
            volatility,
        )

    result = implied_volatility(
        spot_price=SPOT,
        strike_price=STRIKE,
        time_to_expiry=TIME,
        risk_free_rate=RATE,
        option_price=market_price,
        option_type=option_type,
    )

    assert result == pytest.approx(
        volatility,
        abs=1e-6,
    )


def test_implied_volatility_accepts_lowercase_option_type() -> None:
    market_price = black_scholes_call(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    )

    result = implied_volatility(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        market_price,
        "call",
    )

    assert result == pytest.approx(
        VOLATILITY,
        abs=1e-6,
    )


def test_implied_volatility_with_different_market_conditions() -> None:
    spot = 150.0
    strike = 140.0
    time = 0.75
    rate = 0.06
    volatility = 0.28

    market_price = black_scholes_call(
        spot,
        strike,
        time,
        rate,
        volatility,
    )

    result = implied_volatility(
        spot_price=spot,
        strike_price=strike,
        time_to_expiry=time,
        risk_free_rate=rate,
        option_price=market_price,
        option_type="CALL",
    )

    assert result == pytest.approx(
        volatility,
        abs=1e-6,
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "spot_price": 0.0,
            "strike_price": 100.0,
            "time_to_expiry": 1.0,
            "risk_free_rate": 0.05,
            "option_price": 10.0,
            "option_type": "CALL",
        },
        {
            "spot_price": 100.0,
            "strike_price": 0.0,
            "time_to_expiry": 1.0,
            "risk_free_rate": 0.05,
            "option_price": 10.0,
            "option_type": "CALL",
        },
        {
            "spot_price": 100.0,
            "strike_price": 100.0,
            "time_to_expiry": 0.0,
            "risk_free_rate": 0.05,
            "option_price": 10.0,
            "option_type": "CALL",
        },
        {
            "spot_price": 100.0,
            "strike_price": 100.0,
            "time_to_expiry": 1.0,
            "risk_free_rate": 0.05,
            "option_price": 0.0,
            "option_type": "CALL",
        },
    ],
)
def test_invalid_inputs_raise_value_error(
    kwargs: dict[str, float | str],
) -> None:
    with pytest.raises(ValueError):
        implied_volatility(**kwargs)


def test_invalid_option_type() -> None:
    with pytest.raises(ValueError):
        implied_volatility(
            SPOT,
            STRIKE,
            TIME,
            RATE,
            10.0,
            "INVALID",
        )


def test_invalid_initial_volatility() -> None:
    with pytest.raises(ValueError):
        implied_volatility(
            SPOT,
            STRIKE,
            TIME,
            RATE,
            10.0,
            "CALL",
            initial_volatility=0.0,
        )


def test_invalid_tolerance() -> None:
    with pytest.raises(ValueError):
        implied_volatility(
            SPOT,
            STRIKE,
            TIME,
            RATE,
            10.0,
            "CALL",
            tolerance=0.0,
        )


def test_invalid_max_iterations() -> None:
    with pytest.raises(ValueError):
        implied_volatility(
            SPOT,
            STRIKE,
            TIME,
            RATE,
            10.0,
            "CALL",
            max_iterations=0,
        )


def test_call_implied_volatility_from_non_default_initial_guess() -> None:
    market_price = black_scholes_call(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    )

    result = implied_volatility(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        market_price,
        "CALL",
        initial_volatility=0.80,
    )

    assert result == pytest.approx(
        VOLATILITY,
        abs=1e-6,
    )