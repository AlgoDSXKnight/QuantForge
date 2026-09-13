from dataclasses import dataclass


@dataclass(frozen=True)
class OptionLeg:
    option_type: str
    position: str
    strike_price: float
    premium: float
    quantity: int = 1


@dataclass(frozen=True)
class StrategyPayoff:
    underlying_price: float
    payoff: float
    pnl: float


@dataclass(frozen=True)
class StrategyAnalytics:
    net_premium: float
    breakeven_prices: list[float]
    max_profit: float | None
    max_loss: float | None


def _validate_leg(leg: OptionLeg) -> None:
    option_type = leg.option_type.upper()
    position = leg.position.upper()

    if option_type not in {"CALL", "PUT"}:
        raise ValueError("Option type must be CALL or PUT.")

    if position not in {"LONG", "SHORT"}:
        raise ValueError("Position must be LONG or SHORT.")

    if leg.strike_price <= 0:
        raise ValueError("Strike price must be greater than zero.")

    if leg.premium < 0:
        raise ValueError("Premium cannot be negative.")

    if not isinstance(leg.quantity, int):
        raise ValueError("Quantity must be an integer.")

    if leg.quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")


def _validate_underlying_price(
    underlying_price: float,
) -> None:
    if underlying_price < 0:
        raise ValueError(
            "Underlying price cannot be negative."
        )


def _validate_butterfly_strikes(
    lower_strike: float,
    middle_strike: float,
    upper_strike: float,
) -> None:
    """
    Validate the strikes used by a standard butterfly.

    Requirements:

        lower < middle < upper

    and:

        middle - lower == upper - middle
    """

    if (
        lower_strike <= 0
        or middle_strike <= 0
        or upper_strike <= 0
    ):
        raise ValueError(
            "Strike prices must be greater than zero."
        )

    if not (
        lower_strike
        < middle_strike
        < upper_strike
    ):
        raise ValueError(
            "Butterfly strikes must satisfy "
            "lower < middle < upper."
        )

    left_width = (
        middle_strike - lower_strike
    )

    right_width = (
        upper_strike - middle_strike
    )

    if abs(left_width - right_width) > 1e-9:
        raise ValueError(
            "Butterfly strikes must be equally spaced."
        )


def _validate_iron_condor_strikes(
    put_long_strike: float,
    put_short_strike: float,
    call_short_strike: float,
    call_long_strike: float,
) -> None:
    """
    Validate the four strikes used by an iron condor.

    Required ordering:

        put_long < put_short < call_short < call_long
    """

    if any(
        strike <= 0
        for strike in (
            put_long_strike,
            put_short_strike,
            call_short_strike,
            call_long_strike,
        )
    ):
        raise ValueError(
            "Strike prices must be greater than zero."
        )

    if not (
        put_long_strike
        < put_short_strike
        < call_short_strike
        < call_long_strike
    ):
        raise ValueError(
            "Iron condor strikes must satisfy "
            "put_long < put_short < call_short < call_long."
        )


def _validate_iron_butterfly_strikes(
    lower_strike: float,
    middle_strike: float,
    upper_strike: float,
) -> None:
    """
    Validate the three strikes used by an iron butterfly.

    Required ordering:

        lower < middle < upper

    Unlike a standard butterfly, the two wings do not
    need to be equally spaced.
    """

    if (
        lower_strike <= 0
        or middle_strike <= 0
        or upper_strike <= 0
    ):
        raise ValueError(
            "Strike prices must be greater than zero."
        )

    if not (
        lower_strike
        < middle_strike
        < upper_strike
    ):
        raise ValueError(
            "Iron butterfly strikes must satisfy "
            "lower < middle < upper."
        )


# ============================================================================
# Vertical Spreads
# ============================================================================


def bull_call_spread(
    lower_strike: float,
    upper_strike: float,
    long_premium: float,
    short_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Bull Call Spread:

        Long lower-strike call
        Short higher-strike call
    """

    return [
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=lower_strike,
            premium=long_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=upper_strike,
            premium=short_premium,
            quantity=quantity,
        ),
    ]


def bear_call_spread(
    lower_strike: float,
    upper_strike: float,
    short_premium: float,
    long_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Bear Call Spread:

        Short lower-strike call
        Long higher-strike call
    """

    return [
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=lower_strike,
            premium=short_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=upper_strike,
            premium=long_premium,
            quantity=quantity,
        ),
    ]


def bull_put_spread(
    lower_strike: float,
    upper_strike: float,
    long_premium: float,
    short_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Bull Put Spread:

        Short higher-strike put
        Long lower-strike put
    """

    return [
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=upper_strike,
            premium=short_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=lower_strike,
            premium=long_premium,
            quantity=quantity,
        ),
    ]


def bear_put_spread(
    lower_strike: float,
    upper_strike: float,
    long_premium: float,
    short_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Bear Put Spread:

        Long higher-strike put
        Short lower-strike put
    """

    return [
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=upper_strike,
            premium=long_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=lower_strike,
            premium=short_premium,
            quantity=quantity,
        ),
    ]


# ============================================================================
# Straddles
# ============================================================================


def long_straddle(
    strike_price: float,
    call_premium: float,
    put_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Long Straddle:

        Long call
        Long put

    Same strike.
    """

    return [
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=strike_price,
            premium=call_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=strike_price,
            premium=put_premium,
            quantity=quantity,
        ),
    ]


def short_straddle(
    strike_price: float,
    call_premium: float,
    put_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Short Straddle:

        Short call
        Short put

    Same strike.
    """

    return [
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=strike_price,
            premium=call_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=strike_price,
            premium=put_premium,
            quantity=quantity,
        ),
    ]


# ============================================================================
# Strangles
# ============================================================================


def long_strangle(
    put_strike: float,
    call_strike: float,
    put_premium: float,
    call_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Long Strangle:

        Long lower-strike put
        Long higher-strike call
    """

    return [
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=put_strike,
            premium=put_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=call_strike,
            premium=call_premium,
            quantity=quantity,
        ),
    ]


def short_strangle(
    put_strike: float,
    call_strike: float,
    put_premium: float,
    call_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Short Strangle:

        Short lower-strike put
        Short higher-strike call
    """

    return [
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=put_strike,
            premium=put_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=call_strike,
            premium=call_premium,
            quantity=quantity,
        ),
    ]


# ============================================================================
# Butterflies
# ============================================================================


def long_call_butterfly(
    lower_strike: float,
    middle_strike: float,
    upper_strike: float,
    lower_premium: float,
    middle_premium: float,
    upper_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Long Call Butterfly:

        Long 1 lower-strike call
        Short 2 middle-strike calls
        Long 1 upper-strike call

    Requires equally spaced strikes.
    """

    _validate_butterfly_strikes(
        lower_strike,
        middle_strike,
        upper_strike,
    )

    return [
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=lower_strike,
            premium=lower_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=middle_strike,
            premium=middle_premium,
            quantity=quantity * 2,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=upper_strike,
            premium=upper_premium,
            quantity=quantity,
        ),
    ]


def short_call_butterfly(
    lower_strike: float,
    middle_strike: float,
    upper_strike: float,
    lower_premium: float,
    middle_premium: float,
    upper_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Short Call Butterfly:

        Short 1 lower-strike call
        Long 2 middle-strike calls
        Short 1 upper-strike call

    Requires equally spaced strikes.
    """

    _validate_butterfly_strikes(
        lower_strike,
        middle_strike,
        upper_strike,
    )

    return [
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=lower_strike,
            premium=lower_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=middle_strike,
            premium=middle_premium,
            quantity=quantity * 2,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=upper_strike,
            premium=upper_premium,
            quantity=quantity,
        ),
    ]


def long_put_butterfly(
    lower_strike: float,
    middle_strike: float,
    upper_strike: float,
    lower_premium: float,
    middle_premium: float,
    upper_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Long Put Butterfly:

        Long 1 lower-strike put
        Short 2 middle-strike puts
        Long 1 upper-strike put

    Requires equally spaced strikes.
    """

    _validate_butterfly_strikes(
        lower_strike,
        middle_strike,
        upper_strike,
    )

    return [
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=lower_strike,
            premium=lower_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=middle_strike,
            premium=middle_premium,
            quantity=quantity * 2,
        ),
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=upper_strike,
            premium=upper_premium,
            quantity=quantity,
        ),
    ]


def short_put_butterfly(
    lower_strike: float,
    middle_strike: float,
    upper_strike: float,
    lower_premium: float,
    middle_premium: float,
    upper_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Short Put Butterfly:

        Short 1 lower-strike put
        Long 2 middle-strike puts
        Short 1 upper-strike put

    Requires equally spaced strikes.
    """

    _validate_butterfly_strikes(
        lower_strike,
        middle_strike,
        upper_strike,
    )

    return [
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=lower_strike,
            premium=lower_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=middle_strike,
            premium=middle_premium,
            quantity=quantity * 2,
        ),
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=upper_strike,
            premium=upper_premium,
            quantity=quantity,
        ),
    ]


# ============================================================================
# Iron Condors
# ============================================================================


def long_iron_condor(
    put_long_strike: float,
    put_short_strike: float,
    call_short_strike: float,
    call_long_strike: float,
    put_long_premium: float,
    put_short_premium: float,
    call_short_premium: float,
    call_long_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Long Iron Condor:

        Long lower-strike put
        Short higher-strike put
        Short lower-strike call
        Long higher-strike call
    """

    _validate_iron_condor_strikes(
        put_long_strike,
        put_short_strike,
        call_short_strike,
        call_long_strike,
    )

    return [
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=put_long_strike,
            premium=put_long_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=put_short_strike,
            premium=put_short_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=call_short_strike,
            premium=call_short_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=call_long_strike,
            premium=call_long_premium,
            quantity=quantity,
        ),
    ]


def short_iron_condor(
    put_long_strike: float,
    put_short_strike: float,
    call_short_strike: float,
    call_long_strike: float,
    put_long_premium: float,
    put_short_premium: float,
    call_short_premium: float,
    call_long_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Short Iron Condor:

        Short lower-strike put
        Long higher-strike put
        Long lower-strike call
        Short higher-strike call
    """

    _validate_iron_condor_strikes(
        put_long_strike,
        put_short_strike,
        call_short_strike,
        call_long_strike,
    )

    return [
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=put_long_strike,
            premium=put_long_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=put_short_strike,
            premium=put_short_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=call_short_strike,
            premium=call_short_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=call_long_strike,
            premium=call_long_premium,
            quantity=quantity,
        ),
    ]


# ============================================================================
# Iron Butterflies
# ============================================================================


def long_iron_butterfly(
    lower_strike: float,
    middle_strike: float,
    upper_strike: float,
    lower_put_premium: float,
    middle_put_premium: float,
    middle_call_premium: float,
    upper_call_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Long Iron Butterfly:

        Long lower-strike put
        Short middle-strike put
        Short middle-strike call
        Long upper-strike call

    The strikes only need to satisfy:

        lower < middle < upper
    """

    _validate_iron_butterfly_strikes(
        lower_strike,
        middle_strike,
        upper_strike,
    )

    return [
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=lower_strike,
            premium=lower_put_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=middle_strike,
            premium=middle_put_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=middle_strike,
            premium=middle_call_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=upper_strike,
            premium=upper_call_premium,
            quantity=quantity,
        ),
    ]


def short_iron_butterfly(
    lower_strike: float,
    middle_strike: float,
    upper_strike: float,
    lower_put_premium: float,
    middle_put_premium: float,
    middle_call_premium: float,
    upper_call_premium: float,
    quantity: int = 1,
) -> list[OptionLeg]:
    """
    Short Iron Butterfly:

        Short lower-strike put
        Long middle-strike put
        Long middle-strike call
        Short upper-strike call

    The strikes only need to satisfy:

        lower < middle < upper
    """

    _validate_iron_butterfly_strikes(
        lower_strike,
        middle_strike,
        upper_strike,
    )

    return [
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=lower_strike,
            premium=lower_put_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=middle_strike,
            premium=middle_put_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=middle_strike,
            premium=middle_call_premium,
            quantity=quantity,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=upper_strike,
            premium=upper_call_premium,
            quantity=quantity,
        ),
    ]


# ============================================================================
# Core Payoff / P&L Engine
# ============================================================================


def calculate_leg_payoff(
    leg: OptionLeg,
    underlying_price: float,
) -> float:
    """
    Calculate intrinsic payoff of one option leg at expiry.
    """

    _validate_leg(leg)
    _validate_underlying_price(underlying_price)

    option_type = leg.option_type.upper()
    position = leg.position.upper()

    if option_type == "CALL":
        intrinsic_value = max(
            underlying_price - leg.strike_price,
            0.0,
        )
    else:
        intrinsic_value = max(
            leg.strike_price - underlying_price,
            0.0,
        )

    if position == "SHORT":
        intrinsic_value *= -1.0

    return intrinsic_value * leg.quantity


def calculate_leg_pnl(
    leg: OptionLeg,
    underlying_price: float,
) -> float:
    """
    Calculate P&L of one option leg at expiry.
    """

    payoff = calculate_leg_payoff(
        leg=leg,
        underlying_price=underlying_price,
    )

    premium_value = (
        leg.premium * leg.quantity
    )

    if leg.position.upper() == "LONG":
        return payoff - premium_value

    return payoff + premium_value


def calculate_strategy_payoff(
    legs: list[OptionLeg],
    underlying_price: float,
) -> float:
    """
    Calculate total intrinsic payoff of an option strategy.
    """

    if not legs:
        raise ValueError(
            "At least one option leg is required."
        )

    _validate_underlying_price(
        underlying_price
    )

    return sum(
        calculate_leg_payoff(
            leg=leg,
            underlying_price=underlying_price,
        )
        for leg in legs
    )


def calculate_strategy_pnl(
    legs: list[OptionLeg],
    underlying_price: float,
) -> float:
    """
    Calculate total strategy P&L at expiry.
    """

    if not legs:
        raise ValueError(
            "At least one option leg is required."
        )

    _validate_underlying_price(
        underlying_price
    )

    return sum(
        calculate_leg_pnl(
            leg=leg,
            underlying_price=underlying_price,
        )
        for leg in legs
    )


def calculate_strategy_payoff_curve(
    legs: list[OptionLeg],
    underlying_prices: list[float],
) -> list[StrategyPayoff]:
    """
    Calculate strategy payoff and P&L across
    multiple underlying prices.
    """

    if not legs:
        raise ValueError(
            "At least one option leg is required."
        )

    if not underlying_prices:
        raise ValueError(
            "At least one underlying price is required."
        )

    return [
        StrategyPayoff(
            underlying_price=underlying_price,
            payoff=calculate_strategy_payoff(
                legs,
                underlying_price,
            ),
            pnl=calculate_strategy_pnl(
                legs,
                underlying_price,
            ),
        )
        for underlying_price in underlying_prices
    ]


# ============================================================================
# Strategy Analytics
# ============================================================================


def calculate_net_premium(
    legs: list[OptionLeg],
) -> float:
    """
    Calculate net premium paid or received.

    Positive:
        Net premium paid.

    Negative:
        Net premium received.
    """

    if not legs:
        raise ValueError(
            "At least one option leg is required."
        )

    for leg in legs:
        _validate_leg(leg)

    net_premium = 0.0

    for leg in legs:
        premium_value = (
            leg.premium * leg.quantity
        )

        if leg.position.upper() == "LONG":
            net_premium += premium_value
        else:
            net_premium -= premium_value

    return net_premium


def _calculate_pnl_slope(
    legs: list[OptionLeg],
    underlying_price: float,
) -> float:
    """
    Calculate the slope of strategy P&L immediately around
    a given underlying price.
    """

    epsilon = max(
        1e-6,
        underlying_price * 1e-6,
    )

    left_price = max(
        underlying_price - epsilon,
        0.0,
    )

    right_price = (
        underlying_price + epsilon
    )

    left_pnl = calculate_strategy_pnl(
        legs,
        left_price,
    )

    right_pnl = calculate_strategy_pnl(
        legs,
        right_price,
    )

    if right_price == left_price:
        return 0.0

    return (
        right_pnl - left_pnl
    ) / (
        right_price - left_price
    )


def calculate_breakeven_prices(
    legs: list[OptionLeg],
) -> list[float]:
    """
    Calculate strategy breakeven prices at expiry.

    A breakeven is an underlying price where strategy P&L = 0.
    The P&L function is piecewise linear between option strikes,
    so each interval can be solved directly.
    """

    if not legs:
        raise ValueError(
            "At least one option leg is required."
        )

    for leg in legs:
        _validate_leg(leg)

    strikes = sorted(
        {
            leg.strike_price
            for leg in legs
        }
    )

    if not strikes:
        return []

    # Create intervals:
    #
    # [0, K1], [K1, K2], ..., [Kn, terminal]
    #
    # The final interval extends beyond the highest strike.
    terminal_price = strikes[-1] + max(
        strikes[-1],
        1.0,
    )

    boundaries = (
        [0.0]
        + strikes
        + [terminal_price]
    )

    breakevens: list[float] = []

    def add_breakeven(price: float) -> None:
        if price < -1e-9:
            return

        price = max(price, 0.0)

        rounded = round(
            price,
            10,
        )

        if not any(
            abs(existing - rounded) < 1e-9
            for existing in breakevens
        ):
            breakevens.append(rounded)

    # Check every strike/boundary itself.
    for price in boundaries[:-1]:
        pnl = calculate_strategy_pnl(
            legs,
            price,
        )

        if abs(pnl) < 1e-9:
            add_breakeven(price)

    # Solve the linear P&L equation inside every interval.
    for index in range(
        len(boundaries) - 1
    ):
        lower = boundaries[index]
        upper = boundaries[index + 1]

        # Use two interior points rather than only endpoints.
        # This avoids missing a crossing when the P&L happens
        # to have the same sign at both boundaries.
        midpoint = (
            lower + upper
        ) / 2.0

        pnl_lower = calculate_strategy_pnl(
            legs,
            lower,
        )

        pnl_mid = calculate_strategy_pnl(
            legs,
            midpoint,
        )

        pnl_upper = calculate_strategy_pnl(
            legs,
            upper,
        )

        # The P&L is linear in this interval.
        # Determine its slope using the midpoint.
        slope = (
            pnl_upper - pnl_lower
        ) / (
            upper - lower
        )

        if abs(slope) < 1e-12:
            slope = (
                pnl_mid - pnl_lower
            ) / (
                midpoint - lower
            )

        if abs(slope) < 1e-12:
            continue

        breakeven = (
            lower
            - pnl_lower / slope
        )

        # Only accept solutions actually inside
        # this interval.
        if (
            lower - 1e-9
            <= breakeven
            <= upper + 1e-9
        ):
            pnl_at_breakeven = calculate_strategy_pnl(
                legs,
                breakeven,
            )

            if abs(
                pnl_at_breakeven
            ) < 1e-7:
                add_breakeven(
                    breakeven
                )

    # Final interval:
    #
    # [highest strike, infinity)
    #
    # The previous loop only covers the finite terminal
    # boundary. If the final P&L slope leads back to zero
    # beyond that boundary, solve it here.
    final_lower = strikes[-1]

    final_pnl = calculate_strategy_pnl(
        legs,
        final_lower,
    )

    final_slope = _calculate_pnl_slope(
        legs,
        final_lower + max(
            strikes[-1] * 1e-6,
            1e-6,
        ),
    )

    if abs(final_slope) > 1e-12:
        breakeven = (
            final_lower
            - final_pnl / final_slope
        )

        if breakeven >= final_lower - 1e-9:
            pnl_at_breakeven = calculate_strategy_pnl(
                legs,
                breakeven,
            )

            if abs(
                pnl_at_breakeven
            ) < 1e-7:
                add_breakeven(
                    breakeven
                )

    return sorted(breakevens)


def calculate_max_profit(
    legs: list[OptionLeg],
) -> float | None:
    """
    Calculate maximum possible strategy profit.

    Returns None when profit is theoretically unlimited.
    """

    if not legs:
        raise ValueError(
            "At least one option leg is required."
        )

    for leg in legs:
        _validate_leg(leg)

    strikes = sorted(
        {
            leg.strike_price
            for leg in legs
        }
    )

    test_prices = (
        [0.0]
        + strikes
        + [
            strikes[-1]
            + max(
                strikes[-1],
                1.0,
            )
        ]
    )

    pnl_values = [
        calculate_strategy_pnl(
            legs,
            price,
        )
        for price in test_prices
    ]

    terminal_price = test_prices[-1]

    terminal_slope = _calculate_pnl_slope(
        legs,
        terminal_price,
    )

    if terminal_slope > 1e-9:
        return None

    return max(pnl_values)


def calculate_max_loss(
    legs: list[OptionLeg],
) -> float | None:
    """
    Calculate maximum possible strategy loss.

    Returns None when loss is theoretically unlimited.
    """

    if not legs:
        raise ValueError(
            "At least one option leg is required."
        )

    for leg in legs:
        _validate_leg(leg)

    strikes = sorted(
        {
            leg.strike_price
            for leg in legs
        }
    )

    test_prices = (
        [0.0]
        + strikes
        + [
            strikes[-1]
            + max(
                strikes[-1],
                1.0,
            )
        ]
    )

    pnl_values = [
        calculate_strategy_pnl(
            legs,
            price,
        )
        for price in test_prices
    ]

    terminal_price = test_prices[-1]

    terminal_slope = _calculate_pnl_slope(
        legs,
        terminal_price,
    )

    if terminal_slope < -1e-9:
        return None

    return min(pnl_values)


def calculate_strategy_analytics(
    legs: list[OptionLeg],
) -> StrategyAnalytics:
    """
    Calculate the main expiry analytics for an option strategy.
    """

    return StrategyAnalytics(
        net_premium=calculate_net_premium(
            legs
        ),
        breakeven_prices=calculate_breakeven_prices(
            legs
        ),
        max_profit=calculate_max_profit(
            legs
        ),
        max_loss=calculate_max_loss(
            legs
        ),
    )