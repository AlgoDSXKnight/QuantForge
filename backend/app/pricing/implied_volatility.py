from math import exp, isfinite

from app.pricing.black_scholes import black_scholes_call, black_scholes_put
from app.pricing.greeks import vega


def _validate_inputs(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    option_price: float,
) -> None:
    if spot_price <= 0:
        raise ValueError("Spot price must be greater than zero.")

    if strike_price <= 0:
        raise ValueError("Strike price must be greater than zero.")

    if time_to_expiry <= 0:
        raise ValueError("Time to expiry must be greater than zero.")

    if option_price <= 0:
        raise ValueError("Option price must be greater than zero.")


def _validate_market_price(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    option_price: float,
    option_type: str,
) -> None:
    option_type = option_type.upper()

    if option_type not in {"CALL", "PUT"}:
        raise ValueError("Option type must be CALL or PUT.")

    discount_factor = exp(
        -risk_free_rate * time_to_expiry
    )

    if option_type == "CALL":
        lower_bound = max(
            0.0,
            spot_price - strike_price * discount_factor,
        )
        upper_bound = spot_price
    else:
        lower_bound = max(
            0.0,
            strike_price * discount_factor - spot_price,
        )
        upper_bound = strike_price * discount_factor

    if option_price < lower_bound or option_price > upper_bound:
        raise ValueError(
            "Option price is outside the theoretical no-arbitrage bounds."
        )


def _option_price(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    option_type: str,
) -> float:
    if option_type == "CALL":
        return black_scholes_call(
            spot_price,
            strike_price,
            time_to_expiry,
            risk_free_rate,
            volatility,
        )

    return black_scholes_put(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )


def implied_volatility(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    option_price: float,
    option_type: str,
    initial_volatility: float = 0.20,
    tolerance: float = 1e-8,
    max_iterations: int = 100,
) -> float:
    """
    Calculate implied volatility using Newton-Raphson with
    bisection fallback.
    """

    _validate_inputs(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        option_price,
    )

    option_type = option_type.upper()

    _validate_market_price(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        option_price,
        option_type,
    )

    if initial_volatility <= 0:
        raise ValueError(
            "Initial volatility must be greater than zero."
        )

    if tolerance <= 0:
        raise ValueError("Tolerance must be greater than zero.")

    if max_iterations <= 0:
        raise ValueError(
            "Maximum iterations must be greater than zero."
        )

    volatility = initial_volatility

    # Newton-Raphson
    for _ in range(max_iterations):
        price = _option_price(
            spot_price,
            strike_price,
            time_to_expiry,
            risk_free_rate,
            volatility,
            option_type,
        )

        price_difference = price - option_price

        if abs(price_difference) < tolerance:
            return volatility

        current_vega = vega(
            spot_price,
            strike_price,
            time_to_expiry,
            risk_free_rate,
            volatility,
        )

        if current_vega <= 1e-12 or not isfinite(current_vega):
            break

        new_volatility = volatility - (
            price_difference / current_vega
        )

        if new_volatility <= 0 or not isfinite(new_volatility):
            break

        volatility = new_volatility

    # Bisection fallback
    lower_volatility = 1e-8
    upper_volatility = 5.0

    lower_price = _option_price(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        lower_volatility,
        option_type,
    )

    upper_price = _option_price(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        upper_volatility,
        option_type,
    )

    lower_difference = lower_price - option_price
    upper_difference = upper_price - option_price

    if lower_difference * upper_difference > 0:
        raise ValueError(
            "Unable to bracket the implied volatility solution."
        )

    for _ in range(max_iterations):
        middle_volatility = (
            lower_volatility + upper_volatility
        ) / 2.0

        middle_price = _option_price(
            spot_price,
            strike_price,
            time_to_expiry,
            risk_free_rate,
            middle_volatility,
            option_type,
        )

        middle_difference = middle_price - option_price

        if abs(middle_difference) < tolerance:
            return middle_volatility

        if lower_difference * middle_difference <= 0:
            upper_volatility = middle_volatility
            upper_difference = middle_difference
        else:
            lower_volatility = middle_volatility
            lower_difference = middle_difference

    return (
        lower_volatility + upper_volatility
    ) / 2.0