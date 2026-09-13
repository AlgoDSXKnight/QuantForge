import pytest

from app.pricing.black_scholes import (
    black_scholes_call,
    black_scholes_put,
)


def test_black_scholes_call_known_value() -> None:
    price = black_scholes_call(
        spot_price=100.0,
        strike_price=100.0,
        time_to_expiry=1.0,
        risk_free_rate=0.05,
        volatility=0.20,
    )

    assert price == pytest.approx(
        10.4506,
        abs=0.001,
    )


def test_black_scholes_put_known_value() -> None:
    price = black_scholes_put(
        spot_price=100.0,
        strike_price=100.0,
        time_to_expiry=1.0,
        risk_free_rate=0.05,
        volatility=0.20,
    )

    assert price == pytest.approx(
        5.5735,
        abs=0.001,
    )


def test_put_call_parity() -> None:
    spot_price = 100.0
    strike_price = 100.0
    time_to_expiry = 1.0
    risk_free_rate = 0.05
    volatility = 0.20

    call_price = black_scholes_call(
        spot_price=spot_price,
        strike_price=strike_price,
        time_to_expiry=time_to_expiry,
        risk_free_rate=risk_free_rate,
        volatility=volatility,
    )

    put_price = black_scholes_put(
        spot_price=spot_price,
        strike_price=strike_price,
        time_to_expiry=time_to_expiry,
        risk_free_rate=risk_free_rate,
        volatility=volatility,
    )

    left_side = call_price - put_price

    right_side = (
        spot_price
        - strike_price
        * __import__("math").exp(
            -risk_free_rate * time_to_expiry
        )
    )

    assert left_side == pytest.approx(
        right_side,
        abs=0.0001,
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "spot_price": 0.0,
            "strike_price": 100.0,
            "time_to_expiry": 1.0,
            "risk_free_rate": 0.05,
            "volatility": 0.20,
        },
        {
            "spot_price": 100.0,
            "strike_price": 0.0,
            "time_to_expiry": 1.0,
            "risk_free_rate": 0.05,
            "volatility": 0.20,
        },
        {
            "spot_price": 100.0,
            "strike_price": 100.0,
            "time_to_expiry": 0.0,
            "risk_free_rate": 0.05,
            "volatility": 0.20,
        },
        {
            "spot_price": 100.0,
            "strike_price": 100.0,
            "time_to_expiry": 1.0,
            "risk_free_rate": 0.05,
            "volatility": 0.0,
        },
    ],
)
def test_invalid_inputs_raise_value_error(
    kwargs: dict[str, float],
) -> None:
    with pytest.raises(ValueError):
        black_scholes_call(**kwargs)