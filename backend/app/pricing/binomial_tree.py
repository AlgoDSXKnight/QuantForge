from math import exp, sqrt


def _validate_inputs(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    steps: int,
) -> None:
    if spot_price <= 0:
        raise ValueError("Spot price must be greater than zero.")

    if strike_price <= 0:
        raise ValueError("Strike price must be greater than zero.")

    if time_to_expiry <= 0:
        raise ValueError("Time to expiry must be greater than zero.")

    if volatility <= 0:
        raise ValueError("Volatility must be greater than zero.")

    if steps <= 0:
        raise ValueError("Steps must be greater than zero.")

    if not isinstance(steps, int):
        raise ValueError("Steps must be an integer.")


def _calculate_parameters(
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    steps: int,
) -> tuple[float, float, float, float]:
    dt = time_to_expiry / steps

    up_factor = exp(volatility * sqrt(dt))

    down_factor = 1.0 / up_factor

    discount_factor = exp(-risk_free_rate * dt)

    risk_neutral_probability = (
        exp(risk_free_rate * dt) - down_factor
    ) / (up_factor - down_factor)

    return (
        dt,
        up_factor,
        down_factor,
        risk_neutral_probability,
    )


def _calculate_stock_prices(
    spot_price: float,
    up_factor: float,
    down_factor: float,
    steps: int,
) -> list[float]:
    stock_prices = []

    for down_moves in range(steps + 1):
        price = (
            spot_price
            * up_factor ** (steps - down_moves)
            * down_factor ** down_moves
        )

        stock_prices.append(price)

    return stock_prices


def _calculate_option_payoffs(
    stock_prices: list[float],
    strike_price: float,
    option_type: str,
) -> list[float]:
    if option_type == "CALL":
        return [
            max(stock_price - strike_price, 0.0)
            for stock_price in stock_prices
        ]

    return [
        max(strike_price - stock_price, 0.0)
        for stock_price in stock_prices
    ]


def _price_option(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    steps: int,
    option_type: str,
    american: bool,
) -> float:
    _validate_inputs(
        spot_price,
        strike_price,
        time_to_expiry,
        risk_free_rate,
        volatility,
        steps,
    )

    if option_type not in {"CALL", "PUT"}:
        raise ValueError("Option type must be CALL or PUT.")

    (
        dt,
        up_factor,
        down_factor,
        risk_neutral_probability,
    ) = _calculate_parameters(
        time_to_expiry,
        risk_free_rate,
        volatility,
        steps,
    )

    discount_factor = exp(-risk_free_rate * dt)

    stock_prices = _calculate_stock_prices(
        spot_price,
        up_factor,
        down_factor,
        steps,
    )

    option_values = _calculate_option_payoffs(
        stock_prices,
        strike_price,
        option_type,
    )

    for step in range(steps - 1, -1, -1):
        next_stock_prices = []

        for down_moves in range(step + 1):
            stock_price = (
                spot_price
                * up_factor ** (step - down_moves)
                * down_factor ** down_moves
            )

            next_stock_prices.append(stock_price)

        new_option_values = []

        for index in range(step + 1):
            continuation_value = discount_factor * (
                risk_neutral_probability
                * option_values[index]
                + (1.0 - risk_neutral_probability)
                * option_values[index + 1]
            )

            if american:
                if option_type == "CALL":
                    exercise_value = max(
                        next_stock_prices[index] - strike_price,
                        0.0,
                    )
                else:
                    exercise_value = max(
                        strike_price - next_stock_prices[index],
                        0.0,
                    )

                option_value = max(
                    continuation_value,
                    exercise_value,
                )
            else:
                option_value = continuation_value

            new_option_values.append(option_value)

        option_values = new_option_values

    return option_values[0]


def binomial_european_call(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    steps: int = 100,
) -> float:
    """Price a European call option using a Cox-Ross-Rubinstein tree."""

    return _price_option(
        spot_price=spot_price,
        strike_price=strike_price,
        time_to_expiry=time_to_expiry,
        risk_free_rate=risk_free_rate,
        volatility=volatility,
        steps=steps,
        option_type="CALL",
        american=False,
    )


def binomial_european_put(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    steps: int = 100,
) -> float:
    """Price a European put option using a Cox-Ross-Rubinstein tree."""

    return _price_option(
        spot_price=spot_price,
        strike_price=strike_price,
        time_to_expiry=time_to_expiry,
        risk_free_rate=risk_free_rate,
        volatility=volatility,
        steps=steps,
        option_type="PUT",
        american=False,
    )


def binomial_american_call(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    steps: int = 100,
) -> float:
    """Price an American call option using a Cox-Ross-Rubinstein tree."""

    return _price_option(
        spot_price=spot_price,
        strike_price=strike_price,
        time_to_expiry=time_to_expiry,
        risk_free_rate=risk_free_rate,
        volatility=volatility,
        steps=steps,
        option_type="CALL",
        american=True,
    )


def binomial_american_put(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    steps: int = 100,
) -> float:
    """Price an American put option using a Cox-Ross-Rubinstein tree."""

    return _price_option(
        spot_price=spot_price,
        strike_price=strike_price,
        time_to_expiry=time_to_expiry,
        risk_free_rate=risk_free_rate,
        volatility=volatility,
        steps=steps,
        option_type="PUT",
        american=True,
    )