import pytest

from app.pricing.binomial_tree import (
    binomial_american_call,
    binomial_american_put,
    binomial_european_call,
    binomial_european_put,
)
from app.pricing.black_scholes import (
    black_scholes_call,
    black_scholes_put,
)


SPOT = 100.0
STRIKE = 100.0
TIME = 1.0
RATE = 0.05
VOLATILITY = 0.20


def test_european_call_is_close_to_black_scholes() -> None:
    binomial_price = binomial_european_call(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        steps=500,
    )

    black_scholes_price = black_scholes_call(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    )

    assert binomial_price == pytest.approx(
        black_scholes_price,
        abs=0.01,
    )


def test_european_put_is_close_to_black_scholes() -> None:
    binomial_price = binomial_european_put(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        steps=500,
    )

    black_scholes_price = black_scholes_put(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    )

    assert binomial_price == pytest.approx(
        black_scholes_price,
        abs=0.01,
    )


def test_american_put_is_at_least_european_put() -> None:
    european_price = binomial_european_put(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        steps=200,
    )

    american_price = binomial_american_put(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        steps=200,
    )

    assert american_price >= european_price


def test_american_call_is_close_to_european_call_without_dividends() -> None:
    european_price = binomial_european_call(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        steps=200,
    )

    american_price = binomial_american_call(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        steps=200,
    )

    assert american_price == pytest.approx(
        european_price,
        abs=0.01,
    )


@pytest.mark.parametrize(
    "function",
    [
        binomial_european_call,
        binomial_european_put,
        binomial_american_call,
        binomial_american_put,
    ],
)
def test_invalid_spot_price(function) -> None:
    with pytest.raises(ValueError):
        function(
            0.0,
            STRIKE,
            TIME,
            RATE,
            VOLATILITY,
        )


@pytest.mark.parametrize(
    "function",
    [
        binomial_european_call,
        binomial_european_put,
        binomial_american_call,
        binomial_american_put,
    ],
)
def test_invalid_strike_price(function) -> None:
    with pytest.raises(ValueError):
        function(
            SPOT,
            0.0,
            TIME,
            RATE,
            VOLATILITY,
        )


@pytest.mark.parametrize(
    "function",
    [
        binomial_european_call,
        binomial_european_put,
        binomial_american_call,
        binomial_american_put,
    ],
)
def test_invalid_time_to_expiry(function) -> None:
    with pytest.raises(ValueError):
        function(
            SPOT,
            STRIKE,
            0.0,
            RATE,
            VOLATILITY,
        )


@pytest.mark.parametrize(
    "function",
    [
        binomial_european_call,
        binomial_european_put,
        binomial_american_call,
        binomial_american_put,
    ],
)
def test_invalid_volatility(function) -> None:
    with pytest.raises(ValueError):
        function(
            SPOT,
            STRIKE,
            TIME,
            RATE,
            0.0,
        )


@pytest.mark.parametrize(
    "steps",
    [0, -1],
)
def test_invalid_steps(steps: int) -> None:
    with pytest.raises(ValueError):
        binomial_european_call(
            SPOT,
            STRIKE,
            TIME,
            RATE,
            VOLATILITY,
            steps=steps,
        )


def test_non_integer_steps() -> None:
    with pytest.raises(ValueError):
        binomial_european_call(
            SPOT,
            STRIKE,
            TIME,
            RATE,
            VOLATILITY,
            steps=100.5,
        )