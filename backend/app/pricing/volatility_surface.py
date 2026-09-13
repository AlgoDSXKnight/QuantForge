from dataclasses import dataclass

from app.pricing.implied_volatility import implied_volatility


@dataclass(frozen=True)
class OptionObservation:
    strike_price: float
    time_to_expiry: float
    market_price: float
    option_type: str


@dataclass(frozen=True)
class VolatilityPoint:
    strike_price: float
    time_to_expiry: float
    implied_volatility: float
    option_type: str


@dataclass(frozen=True)
class VolatilitySmile:
    time_to_expiry: float
    points: list[VolatilityPoint]


@dataclass(frozen=True)
class VolatilityTermStructurePoint:
    time_to_expiry: float
    implied_volatility: float


def _validate_observation(
    observation: OptionObservation,
) -> None:
    if observation.strike_price <= 0:
        raise ValueError(
            "Strike price must be greater than zero."
        )

    if observation.time_to_expiry <= 0:
        raise ValueError(
            "Time to expiry must be greater than zero."
        )

    if observation.market_price <= 0:
        raise ValueError(
            "Market price must be greater than zero."
        )

    if observation.option_type.upper() not in {
        "CALL",
        "PUT",
    }:
        raise ValueError(
            "Option type must be CALL or PUT."
        )


def calculate_volatility_point(
    spot_price: float,
    risk_free_rate: float,
    observation: OptionObservation,
) -> VolatilityPoint:
    """
    Calculate implied volatility for one option observation.
    """

    _validate_observation(observation)

    implied_vol = implied_volatility(
        spot_price=spot_price,
        strike_price=observation.strike_price,
        time_to_expiry=observation.time_to_expiry,
        risk_free_rate=risk_free_rate,
        option_price=observation.market_price,
        option_type=observation.option_type,
    )

    return VolatilityPoint(
        strike_price=observation.strike_price,
        time_to_expiry=observation.time_to_expiry,
        implied_volatility=implied_vol,
        option_type=observation.option_type.upper(),
    )


def build_volatility_surface(
    spot_price: float,
    risk_free_rate: float,
    observations: list[OptionObservation],
) -> list[VolatilityPoint]:
    """
    Convert option-market observations into implied-volatility points.

    Each point represents:

        (strike, expiry) -> implied volatility
    """

    if spot_price <= 0:
        raise ValueError(
            "Spot price must be greater than zero."
        )

    if not observations:
        raise ValueError(
            "At least one option observation is required."
        )

    return [
        calculate_volatility_point(
            spot_price=spot_price,
            risk_free_rate=risk_free_rate,
            observation=observation,
        )
        for observation in observations
    ]


def group_by_expiry(
    points: list[VolatilityPoint],
) -> dict[float, list[VolatilityPoint]]:
    """
    Group volatility points by time to expiry.
    """

    grouped: dict[float, list[VolatilityPoint]] = {}

    for point in points:
        grouped.setdefault(
            point.time_to_expiry,
            [],
        ).append(point)

    for expiry_points in grouped.values():
        expiry_points.sort(
            key=lambda point: point.strike_price
        )

    return dict(sorted(grouped.items()))


def group_by_strike(
    points: list[VolatilityPoint],
) -> dict[float, list[VolatilityPoint]]:
    """
    Group volatility points by strike price.
    """

    grouped: dict[float, list[VolatilityPoint]] = {}

    for point in points:
        grouped.setdefault(
            point.strike_price,
            [],
        ).append(point)

    for strike_points in grouped.values():
        strike_points.sort(
            key=lambda point: point.time_to_expiry
        )

    return dict(sorted(grouped.items()))


def calculate_volatility_smile(
    points: list[VolatilityPoint],
    time_to_expiry: float,
) -> VolatilitySmile:
    """
    Return the volatility smile for one expiry.
    """

    if time_to_expiry <= 0:
        raise ValueError(
            "Time to expiry must be greater than zero."
        )

    expiry_points = [
        point
        for point in points
        if point.time_to_expiry == time_to_expiry
    ]

    if not expiry_points:
        raise ValueError(
            "No volatility points found for the requested expiry."
        )

    expiry_points.sort(
        key=lambda point: point.strike_price
    )

    return VolatilitySmile(
        time_to_expiry=time_to_expiry,
        points=expiry_points,
    )


def calculate_skew(
    points: list[VolatilityPoint],
    time_to_expiry: float,
    lower_strike: float,
    upper_strike: float,
) -> float:
    """
    Calculate volatility skew between two strikes.
    """

    if lower_strike <= 0 or upper_strike <= 0:
        raise ValueError(
            "Strike prices must be greater than zero."
        )

    if lower_strike >= upper_strike:
        raise ValueError(
            "Lower strike must be less than upper strike."
        )

    smile = calculate_volatility_smile(
        points,
        time_to_expiry,
    )

    lower_point = next(
        (
            point
            for point in smile.points
            if point.strike_price == lower_strike
        ),
        None,
    )

    upper_point = next(
        (
            point
            for point in smile.points
            if point.strike_price == upper_strike
        ),
        None,
    )

    if lower_point is None or upper_point is None:
        raise ValueError(
            "Both requested strikes must exist in the volatility surface."
        )

    return (
        upper_point.implied_volatility
        - lower_point.implied_volatility
    ) / (
        upper_strike - lower_strike
    )


def calculate_term_structure(
    points: list[VolatilityPoint],
    strike_price: float,
) -> list[VolatilityTermStructurePoint]:
    """
    Calculate the volatility term structure for one strike.
    """

    if strike_price <= 0:
        raise ValueError(
            "Strike price must be greater than zero."
        )

    strike_points = [
        point
        for point in points
        if point.strike_price == strike_price
    ]

    if not strike_points:
        raise ValueError(
            "No volatility points found for the requested strike."
        )

    strike_points.sort(
        key=lambda point: point.time_to_expiry
    )

    return [
        VolatilityTermStructurePoint(
            time_to_expiry=point.time_to_expiry,
            implied_volatility=point.implied_volatility,
        )
        for point in strike_points
    ]


def _find_bracketing_values(
    values: list[float],
    target: float,
) -> tuple[float, float]:
    """
    Find the two values surrounding a target.

    Exact matches return the same value twice.
    """

    sorted_values = sorted(set(values))

    if target < sorted_values[0]:
        raise ValueError(
            "Target is below the interpolation range."
        )

    if target > sorted_values[-1]:
        raise ValueError(
            "Target is above the interpolation range."
        )

    for index in range(len(sorted_values) - 1):
        lower = sorted_values[index]
        upper = sorted_values[index + 1]

        if lower <= target <= upper:
            return lower, upper

    return sorted_values[-1], sorted_values[-1]


def _interpolate_linear(
    x1: float,
    x2: float,
    y1: float,
    y2: float,
    x: float,
) -> float:
    """
    Perform one-dimensional linear interpolation.
    """

    if x1 == x2:
        return y1

    weight = (x - x1) / (x2 - x1)

    return y1 + weight * (y2 - y1)


def interpolate_implied_volatility(
    points: list[VolatilityPoint],
    strike_price: float,
    time_to_expiry: float,
    option_type: str = "CALL",
) -> float:
    """
    Estimate implied volatility at an arbitrary strike and expiry
    using bilinear interpolation.

    The target must lie inside the observed strike/expiry range.

    For a rectangular grid:

        IV(K,T)

    is obtained by first interpolating across strike for the
    surrounding expiries, then interpolating those results
    across time.

    Exact observed points are returned directly.
    """

    if not points:
        raise ValueError(
            "At least one volatility point is required."
        )

    if strike_price <= 0:
        raise ValueError(
            "Strike price must be greater than zero."
        )

    if time_to_expiry <= 0:
        raise ValueError(
            "Time to expiry must be greater than zero."
        )

    option_type = option_type.upper()

    if option_type not in {"CALL", "PUT"}:
        raise ValueError(
            "Option type must be CALL or PUT."
        )

    filtered_points = [
        point
        for point in points
        if point.option_type == option_type
    ]

    if not filtered_points:
        raise ValueError(
            "No volatility points found for the requested option type."
        )

    strikes = [
        point.strike_price
        for point in filtered_points
    ]

    expiries = [
        point.time_to_expiry
        for point in filtered_points
    ]

    lower_strike, upper_strike = _find_bracketing_values(
        strikes,
        strike_price,
    )

    lower_expiry, upper_expiry = _find_bracketing_values(
        expiries,
        time_to_expiry,
    )

    def get_point(
        strike: float,
        expiry: float,
    ) -> VolatilityPoint:
        matches = [
            point
            for point in filtered_points
            if point.strike_price == strike
            and point.time_to_expiry == expiry
        ]

        if not matches:
            raise ValueError(
                "Volatility surface does not contain a complete "
                "interpolation grid."
            )

        return matches[0]

    lower_left = get_point(
        lower_strike,
        lower_expiry,
    )

    lower_right = get_point(
        upper_strike,
        lower_expiry,
    )

    upper_left = get_point(
        lower_strike,
        upper_expiry,
    )

    upper_right = get_point(
        upper_strike,
        upper_expiry,
    )

    lower_expiry_iv = _interpolate_linear(
        lower_strike,
        upper_strike,
        lower_left.implied_volatility,
        lower_right.implied_volatility,
        strike_price,
    )

    upper_expiry_iv = _interpolate_linear(
        lower_strike,
        upper_strike,
        upper_left.implied_volatility,
        upper_right.implied_volatility,
        strike_price,
    )

    return _interpolate_linear(
        lower_expiry,
        upper_expiry,
        lower_expiry_iv,
        upper_expiry_iv,
        time_to_expiry,
    )