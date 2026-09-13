import pytest

from app.pricing.greeks import (
    call_delta,
    put_delta,
    gamma,
    vega,
    call_theta,
    put_theta,
    call_rho,
    put_rho,
)


SPOT = 100.0
STRIKE = 100.0
TIME = 1.0
RATE = 0.05
VOLATILITY = 0.20


def test_call_delta_known_value() -> None:
    assert call_delta(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    ) == pytest.approx(0.6368, abs=0.0001)


def test_put_delta_known_value() -> None:
    assert put_delta(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    ) == pytest.approx(-0.3632, abs=0.0001)


def test_gamma_known_value() -> None:
    assert gamma(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    ) == pytest.approx(0.01876, abs=0.00001)


def test_vega_known_value() -> None:
    assert vega(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    ) == pytest.approx(37.524, abs=0.001)


def test_call_theta_known_value() -> None:
    assert call_theta(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    ) == pytest.approx(-6.414, abs=0.001)


def test_put_theta_known_value() -> None:
    assert put_theta(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    ) == pytest.approx(-1.658, abs=0.001)


def test_call_rho_known_value() -> None:
    assert call_rho(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    ) == pytest.approx(53.232, abs=0.001)


def test_put_rho_known_value() -> None:
    assert put_rho(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    ) == pytest.approx(-41.890, abs=0.001)


def test_call_put_delta_relationship() -> None:
    assert call_delta(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    ) - put_delta(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    ) == pytest.approx(1.0, abs=0.0001)


def test_call_put_gamma_are_equal() -> None:
    call_gamma = gamma(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    )

    put_gamma = gamma(
        SPOT,
        STRIKE,
        TIME,
        RATE,
        VOLATILITY,
    )

    assert call_gamma == pytest.approx(
        put_gamma,
        abs=0.000001,
    )


@pytest.mark.parametrize(
    "function",
    [
        call_delta,
        put_delta,
        gamma,
        vega,
        call_theta,
        put_theta,
        call_rho,
        put_rho,
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
        