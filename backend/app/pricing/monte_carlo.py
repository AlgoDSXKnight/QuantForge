from dataclasses import dataclass
from math import exp, sqrt
import random


@dataclass(frozen=True)
class MonteCarloResult:
    price: float
    standard_error: float
    confidence_interval_low: float
    confidence_interval_high: float
    simulations: int


def _validate_inputs(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    simulations: int,
) -> None:
    if spot_price <= 0:
        raise ValueError("Spot price must be greater than zero.")

    if strike_price <= 0:
        raise ValueError("Strike price must be greater than zero.")

    if time_to_expiry <= 0:
        raise ValueError("Time to expiry must be greater than zero.")

    if volatility <= 0:
        raise ValueError("Volatility must be greater than zero.")

    if simulations <= 1:
        raise ValueError(
            "Simulations must be greater than one."
        )

    if not isinstance(simulations, int):
        raise ValueError(
            "Simulations must be an integer."
        )


def _simulate_terminal_price(
    spot_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    rng: random.Random,
) -> float:
    random_variable = rng.gauss(0.0, 1.0)

    return spot_price * exp(
        (
            risk_free_rate
            - 0.5 * volatility**2
        )
        * time_to_expiry
        + volatility
        * sqrt(time_to_expiry)
        * random_variable
    )


def _calculate_payoff(
    terminal_price: float,
    strike_price: float,
    option_type: str,
) -> float:
    if option_type == "CALL":
        return max(
            terminal_price - strike_price,
            0.0,
        )

    return max(
        strike_price - terminal_price,
        0.0,
    )


def monte_carlo_option_price(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    option_type: str,
    simulations: int = 100_000,
    seed: int | None = None,
) -> float:
    """
    Estimate a European option price using Monte Carlo simulation.
    """

    result = monte_carlo_option_analysis(
        spot_price=spot_price,
        strike_price=strike_price,
        time_to_expiry=time_to_expiry,
        risk_free_rate=risk_free_rate,
        volatility=volatility,
        option_type=option_type,
        simulations=simulations,
        seed=seed,
    )

    return result.price


def monte_carlo_option_analysis(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    option_type: str,
    simulations: int = 100_000,
    seed: int | None = None,
) -> MonteCarloResult:
    """
    Estimate a European option price and its statistical uncertainty.
    """

    _validate_inputs(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
        simulations,
    )

    option_type = option_type.upper()

    if option_type not in {"CALL", "PUT"}:
        raise ValueError(
            "Option type must be CALL or PUT."
        )

    rng = random.Random(seed)

    total_payoff = 0.0
    total_squared_payoff = 0.0

    for _ in range(simulations):
        terminal_price = _simulate_terminal_price(
            spot_price,
            time_to_expiry,
            risk_free_rate,
            volatility,
            rng,
        )

        payoff = _calculate_payoff(
            terminal_price,
            strike_price,
            option_type,
        )

        total_payoff += payoff
        total_squared_payoff += payoff**2

    mean_payoff = total_payoff / simulations

    sample_variance = (
        total_squared_payoff
        - simulations * mean_payoff**2
    ) / (simulations - 1)

    sample_standard_deviation = sqrt(
        max(sample_variance, 0.0)
    )

    standard_error = (
        sample_standard_deviation
        / sqrt(simulations)
    )

    discount_factor = exp(
        -risk_free_rate * time_to_expiry
    )

    price = discount_factor * mean_payoff

    discounted_standard_error = (
        discount_factor * standard_error
    )

    confidence_interval_low = (
        price - 1.96 * discounted_standard_error
    )

    confidence_interval_high = (
        price + 1.96 * discounted_standard_error
    )

    return MonteCarloResult(
        price=price,
        standard_error=discounted_standard_error,
        confidence_interval_low=confidence_interval_low,
        confidence_interval_high=confidence_interval_high,
        simulations=simulations,
    )