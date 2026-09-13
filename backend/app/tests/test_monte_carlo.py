import pytest

from app.pricing.black_scholes import (
    black_scholes_call,
    black_scholes_put,
)
from app.pricing.monte_carlo import (
    MonteCarloResult,
    monte_carlo_option_analysis,
    monte_carlo_option_price,
)


SPOT = 100.0
STRIKE = 100.0
TIME = 1.0
RATE = 0.05
VOLATILITY = 0.20


def test_monte_carlo_call_is_close_to_black_scholes() -> None:
    monte_carlo_price = monte_carlo_option_price(
        spot_price=SPOT,
        strike_price=STRIKE,
        time_to_expiry=TIME,
        risk_free_rate=RATE,
        volatility=VOLATILITY,
        option_type="CALL",
        simulations=200_000,
        seed=42,
    )

    black_scholes_price = black_scholes_call(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    )

    assert monte_carlo_price == pytest.approx(
        black_scholes_price,
        abs=0.15,
    )


def test_monte_carlo_put_is_close_to_black_scholes() -> None:
    monte_carlo_price = monte_carlo_option_price(
        spot_price=SPOT,
        strike_price=STRIKE,
        time_to_expiry=TIME,
        risk_free_rate=RATE,
        volatility=VOLATILITY,
        option_type="PUT",
        simulations=200_000,
        seed=42,
    )

    black_scholes_price = black_scholes_put(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    )

    assert monte_carlo_price == pytest.approx(
        black_scholes_price,
        abs=0.15,
    )


def test_same_seed_produces_same_result() -> None:
    first_price = monte_carlo_option_price(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        "CALL",
        simulations=10_000,
        seed=123,
    )

    second_price = monte_carlo_option_price(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        "CALL",
        simulations=10_000,
        seed=123,
    )

    assert first_price == second_price


def test_different_seed_can_produce_different_result() -> None:
    first_price = monte_carlo_option_price(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        "CALL",
        simulations=10_000,
        seed=123,
    )

    second_price = monte_carlo_option_price(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        "CALL",
        simulations=10_000,
        seed=456,
    )

    assert first_price != second_price


@pytest.mark.parametrize(
    "option_type",
    ["CALL", "PUT"],
)
def test_option_price_is_non_negative(
    option_type: str,
) -> None:
    price = monte_carlo_option_price(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        option_type,
        simulations=10_000,
        seed=42,
    )

    assert price >= 0.0


def test_analysis_returns_monte_carlo_result() -> None:
    result = monte_carlo_option_analysis(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        "CALL",
        simulations=10_000,
        seed=42,
    )

    assert isinstance(result, MonteCarloResult)
    assert result.simulations == 10_000


def test_standard_error_is_positive() -> None:
    result = monte_carlo_option_analysis(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        "CALL",
        simulations=10_000,
        seed=42,
    )

    assert result.standard_error > 0.0


def test_confidence_interval_contains_price() -> None:
    result = monte_carlo_option_analysis(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        "CALL",
        simulations=10_000,
        seed=42,
    )

    assert (
        result.confidence_interval_low
        <= result.price
        <= result.confidence_interval_high
    )


def test_confidence_interval_has_expected_width() -> None:
    result = monte_carlo_option_analysis(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        "CALL",
        simulations=10_000,
        seed=42,
    )

    expected_half_width = (
        1.96 * result.standard_error
    )

    actual_half_width = (
        result.confidence_interval_high
        - result.price
    )

    assert actual_half_width == pytest.approx(
        expected_half_width,
        abs=1e-12,
    )


def test_more_simulations_reduce_standard_error() -> None:
    low_simulation_result = monte_carlo_option_analysis(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        "CALL",
        simulations=10_000,
        seed=42,
    )

    high_simulation_result = monte_carlo_option_analysis(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        "CALL",
        simulations=40_000,
        seed=42,
    )

    assert (
        high_simulation_result.standard_error
        < low_simulation_result.standard_error
    )


def test_standard_error_follows_sqrt_n_relationship() -> None:
    low_simulation_result = monte_carlo_option_analysis(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        "CALL",
        simulations=10_000,
        seed=42,
    )

    high_simulation_result = monte_carlo_option_analysis(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
        "CALL",
        simulations=40_000,
        seed=42,
    )

    ratio = (
        low_simulation_result.standard_error
        / high_simulation_result.standard_error
    )

    assert ratio == pytest.approx(
        2.0,
        abs=0.15,
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "spot_price": 0.0,
            "strike_price": STRIKE,
            "time_to_expiry": TIME,
            "risk_free_rate": RATE,
            "volatility": VOLATILITY,
            "option_type": "CALL",
        },
        {
            "spot_price": SPOT,
            "strike_price": 0.0,
            "time_to_expiry": TIME,
            "risk_free_rate": RATE,
            "volatility": VOLATILITY,
            "option_type": "CALL",
        },
        {
            "spot_price": SPOT,
            "strike_price": STRIKE,
            "time_to_expiry": 0.0,
            "risk_free_rate": RATE,
            "volatility": VOLATILITY,
            "option_type": "CALL",
        },
        {
            "spot_price": SPOT,
            "strike_price": STRIKE,
            "time_to_expiry": TIME,
            "risk_free_rate": RATE,
            "volatility": 0.0,
            "option_type": "CALL",
        },
        {
            "spot_price": SPOT,
            "strike_price": STRIKE,
            "time_to_expiry": TIME,
            "risk_free_rate": RATE,
            "volatility": VOLATILITY,
            "option_type": "INVALID",
        },
    ],
)
def test_invalid_inputs_raise_value_error(
    kwargs: dict[str, float | str],
) -> None:
    with pytest.raises(ValueError):
        monte_carlo_option_price(**kwargs)


@pytest.mark.parametrize(
    "simulations",
    [0, 1, -1],
)
def test_invalid_simulations(
    simulations: int,
) -> None:
    with pytest.raises(ValueError):
        monte_carlo_option_price(
            SPOT,
            STRIKE,
            TIME,
            RATE,
            VOLATILITY,
            "CALL",
            simulations=simulations,
        )


def test_non_integer_simulations() -> None:
    with pytest.raises(ValueError):
        monte_carlo_option_price(
            SPOT,
            STRIKE,
            TIME,
            RATE,
            VOLATILITY,
            "CALL",
            simulations=1000.5,
        )