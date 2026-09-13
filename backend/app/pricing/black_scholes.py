from math import exp, log, sqrt, erf


def _validate_inputs(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
) -> None:
    if spot_price <= 0:
        raise ValueError("Spot price must be greater than zero.")

    if strike_price <= 0:
        raise ValueError("Strike price must be greater than zero.")

    if time_to_expiry <= 0:
        raise ValueError("Time to expiry must be greater than zero.")

    if volatility <= 0:
        raise ValueError("Volatility must be greater than zero.")


def _normal_cdf(x: float) -> float:
    """
    Standard normal cumulative distribution function.
    """

    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _calculate_d1_d2(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
) -> tuple[float, float]:

    d1 = (
        log(spot_price / strike_price)
        + (
            risk_free_rate
            + 0.5 * volatility**2
        )
        * time_to_expiry
    ) / (
        volatility * sqrt(time_to_expiry)
    )

    d2 = d1 - volatility * sqrt(time_to_expiry)

    return d1, d2


def black_scholes_call(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
) -> float:
    """
    Calculate the theoretical price of a European call option
    using the Black-Scholes model.

    Parameters:
        spot_price: Current underlying price (S)
        strike_price: Option strike price (K)
        time_to_expiry: Time to expiry in years (T)
        risk_free_rate: Continuously compounded risk-free rate (r)
        volatility: Annualized volatility (sigma)

    Returns:
        Theoretical European call option price.
    """

    _validate_inputs(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    d1, d2 = _calculate_d1_d2(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    return (
        spot_price * _normal_cdf(d1)
        - strike_price
        * exp(-risk_free_rate * time_to_expiry)
        * _normal_cdf(d2)
    )


def black_scholes_put(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
) -> float:
    """
    Calculate the theoretical price of a European put option
    using the Black-Scholes model.

    Returns:
        Theoretical European put option price.
    """

    _validate_inputs(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    d1, d2 = _calculate_d1_d2(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    return (
        strike_price
        * exp(-risk_free_rate * time_to_expiry)
        * _normal_cdf(-d2)
        - spot_price
        * _normal_cdf(-d1)
    )