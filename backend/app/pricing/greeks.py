from math import exp, log, pi, sqrt, erf


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


def _normal_pdf(x: float) -> float:
    """Standard normal probability density function."""
    return exp(-0.5 * x**2) / sqrt(2.0 * pi)


def _normal_cdf(x: float) -> float:
    """Standard normal cumulative distribution function."""
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
        + (risk_free_rate + 0.5 * volatility**2) * time_to_expiry
    ) / (volatility * sqrt(time_to_expiry))

    d2 = d1 - volatility * sqrt(time_to_expiry)

    return d1, d2


def call_delta(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
) -> float:
    """Calculate Delta of a European call option."""
    _validate_inputs(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    d1, _ = _calculate_d1_d2(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    return _normal_cdf(d1)


def put_delta(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
) -> float:
    """Calculate Delta of a European put option."""
    _validate_inputs(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    d1, _ = _calculate_d1_d2(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    return _normal_cdf(d1) - 1.0


def gamma(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
) -> float:
    """Calculate Gamma for a European call or put option."""
    _validate_inputs(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    d1, _ = _calculate_d1_d2(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    return _normal_pdf(d1) / (
        spot_price * volatility * sqrt(time_to_expiry)
    )


def vega(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
) -> float:
    """Calculate Vega for a European call or put option."""
    _validate_inputs(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    d1, _ = _calculate_d1_d2(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    return spot_price * _normal_pdf(d1) * sqrt(time_to_expiry)


def call_theta(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
) -> float:
    """Calculate Theta of a European call option."""
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

    first_term = -(
        spot_price
        * _normal_pdf(d1)
        * volatility
        / (2.0 * sqrt(time_to_expiry))
    )

    second_term = -(
        risk_free_rate
        * strike_price
        * exp(-risk_free_rate * time_to_expiry)
        * _normal_cdf(d2)
    )

    return first_term + second_term


def put_theta(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
) -> float:
    """Calculate Theta of a European put option."""
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

    first_term = -(
        spot_price
        * _normal_pdf(d1)
        * volatility
        / (2.0 * sqrt(time_to_expiry))
    )

    second_term = (
        risk_free_rate
        * strike_price
        * exp(-risk_free_rate * time_to_expiry)
        * _normal_cdf(-d2)
    )

    return first_term + second_term


def call_rho(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
) -> float:
    """Calculate Rho of a European call option."""
    _validate_inputs(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    _, d2 = _calculate_d1_d2(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    return (
        strike_price
        * time_to_expiry
        * exp(-risk_free_rate * time_to_expiry)
        * _normal_cdf(d2)
    )


def put_rho(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
) -> float:
    """Calculate Rho of a European put option."""
    _validate_inputs(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    _, d2 = _calculate_d1_d2(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
    )

    return -(
        strike_price
        * time_to_expiry
        * exp(-risk_free_rate * time_to_expiry)
        * _normal_cdf(-d2)
    )
    