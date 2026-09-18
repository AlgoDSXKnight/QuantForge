from dataclasses import dataclass

from app.pricing.volatility_surface import VolatilityPoint


@dataclass(frozen=True)
class SurfaceStatistics:
    point_count: int
    average_iv: float
    minimum_iv: float
    maximum_iv: float
    iv_range: float


@dataclass(frozen=True)
class ExpirationStatistics:
    time_to_expiry: float
    point_count: int
    average_iv: float
    minimum_iv: float
    maximum_iv: float
    atm_iv: float | None
    call_iv: float | None
    put_iv: float | None


@dataclass(frozen=True)
class TermStructureStatistics:
    first_time_to_expiry: float
    first_iv: float
    last_time_to_expiry: float
    last_iv: float
    absolute_change: float
    relative_change: float
    slope: float


@dataclass(frozen=True)
class SmileStatistics:
    time_to_expiry: float
    atm_strike: float
    atm_iv: float
    lower_strike: float | None
    lower_iv: float | None
    upper_strike: float | None
    upper_iv: float | None
    skew: float | None


@dataclass(frozen=True)
class SurfaceDataQuality:
    point_count: int
    expiration_count: int
    strike_count: int
    duplicate_count: int
    duplicate_keys: list[tuple[float, float, str]]


def calculate_surface_statistics(
    points: list[VolatilityPoint],
) -> SurfaceStatistics:
    """Calculate overall statistics for a volatility surface."""
    if not points:
        raise ValueError(
            "At least one volatility point is required."
        )

    ivs = [
        point.implied_volatility
        for point in points
    ]

    minimum_iv = min(ivs)
    maximum_iv = max(ivs)

    return SurfaceStatistics(
        point_count=len(points),
        average_iv=sum(ivs) / len(ivs),
        minimum_iv=minimum_iv,
        maximum_iv=maximum_iv,
        iv_range=maximum_iv - minimum_iv,
    )


def _average(values: list[float]) -> float | None:
    if not values:
        return None

    return sum(values) / len(values)


def _nearest_atm_iv(
    points: list[VolatilityPoint],
) -> float | None:
    if not points:
        return None

    strikes = sorted(
        {point.strike_price for point in points}
    )

    if not strikes:
        return None

    middle_index = len(strikes) // 2

    if len(strikes) % 2 == 1:
        atm_strike = strikes[middle_index]
    else:
        atm_strike = (
            strikes[middle_index - 1]
            + strikes[middle_index]
        ) / 2.0

    nearest = min(
        points,
        key=lambda point: abs(
            point.strike_price - atm_strike
        ),
    )

    return nearest.implied_volatility


def calculate_expiration_statistics(
    points: list[VolatilityPoint],
) -> list[ExpirationStatistics]:
    """Calculate volatility statistics for every expiry."""
    if not points:
        raise ValueError(
            "At least one volatility point is required."
        )

    expirations = sorted(
        {
            point.time_to_expiry
            for point in points
        }
    )

    result: list[ExpirationStatistics] = []

    for expiry in expirations:
        expiry_points = [
            point
            for point in points
            if point.time_to_expiry == expiry
        ]

        ivs = [
            point.implied_volatility
            for point in expiry_points
        ]

        call_ivs = [
            point.implied_volatility
            for point in expiry_points
            if point.option_type == "CALL"
        ]

        put_ivs = [
            point.implied_volatility
            for point in expiry_points
            if point.option_type == "PUT"
        ]

        result.append(
            ExpirationStatistics(
                time_to_expiry=expiry,
                point_count=len(expiry_points),
                average_iv=sum(ivs) / len(ivs),
                minimum_iv=min(ivs),
                maximum_iv=max(ivs),
                atm_iv=_nearest_atm_iv(expiry_points),
                call_iv=_average(call_ivs),
                put_iv=_average(put_ivs),
            )
        )

    return result


def calculate_term_structure_statistics(
    points: list[VolatilityPoint],
    strike_price: float,
) -> TermStructureStatistics:
    """Calculate statistics describing IV across expirations."""
    if strike_price <= 0:
        raise ValueError(
            "Strike price must be greater than zero."
        )

    matching = [
        point
        for point in points
        if point.strike_price == strike_price
    ]

    unique_expirations = {
        point.time_to_expiry
        for point in matching
    }

    if len(unique_expirations) < 2:
        raise ValueError(
            "At least two expirations are required."
        )

    matching.sort(
        key=lambda point: point.time_to_expiry
    )

    first = matching[0]
    last = matching[-1]

    absolute_change = (
        last.implied_volatility
        - first.implied_volatility
    )

    if first.implied_volatility == 0:
        relative_change = 0.0
    else:
        relative_change = (
            absolute_change
            / first.implied_volatility
        )

    time_difference = (
        last.time_to_expiry
        - first.time_to_expiry
    )

    if time_difference <= 0:
        raise ValueError(
            "Expiration times must be distinct."
        )

    slope = absolute_change / time_difference

    return TermStructureStatistics(
        first_time_to_expiry=first.time_to_expiry,
        first_iv=first.implied_volatility,
        last_time_to_expiry=last.time_to_expiry,
        last_iv=last.implied_volatility,
        absolute_change=absolute_change,
        relative_change=relative_change,
        slope=slope,
    )


def calculate_smile_statistics(
    points: list[VolatilityPoint],
    time_to_expiry: float,
) -> SmileStatistics:
    """Calculate basic statistics for one volatility smile."""
    if time_to_expiry <= 0:
        raise ValueError(
            "Time to expiry must be greater than zero."
        )

    smile_points = [
        point
        for point in points
        if point.time_to_expiry == time_to_expiry
    ]

    if not smile_points:
        raise ValueError(
            "No volatility points found for the requested expiry."
        )

    strikes = sorted(
        {
            point.strike_price
            for point in smile_points
        }
    )

    atm_strike = min(
        strikes,
        key=lambda strike: abs(
            strike
            - sum(strikes) / len(strikes)
        ),
    )

    atm_points = [
        point
        for point in smile_points
        if point.strike_price == atm_strike
    ]

    atm_iv = sum(
        point.implied_volatility
        for point in atm_points
    ) / len(atm_points)

    lower_strikes = [
        strike
        for strike in strikes
        if strike < atm_strike
    ]

    upper_strikes = [
        strike
        for strike in strikes
        if strike > atm_strike
    ]

    lower_strike = (
        max(lower_strikes)
        if lower_strikes
        else None
    )

    upper_strike = (
        min(upper_strikes)
        if upper_strikes
        else None
    )

    lower_points = [
        point
        for point in smile_points
        if point.strike_price == lower_strike
    ]

    upper_points = [
        point
        for point in smile_points
        if point.strike_price == upper_strike
    ]

    lower_iv = (
        sum(point.implied_volatility for point in lower_points)
        / len(lower_points)
        if lower_points
        else None
    )

    upper_iv = (
        sum(point.implied_volatility for point in upper_points)
        / len(upper_points)
        if upper_points
        else None
    )

    skew = None

    if (
        lower_iv is not None
        and upper_iv is not None
        and lower_strike is not None
        and upper_strike is not None
    ):
        skew = (
            upper_iv - lower_iv
        ) / (
            upper_strike - lower_strike
        )

    return SmileStatistics(
        time_to_expiry=time_to_expiry,
        atm_strike=atm_strike,
        atm_iv=atm_iv,
        lower_strike=lower_strike,
        lower_iv=lower_iv,
        upper_strike=upper_strike,
        upper_iv=upper_iv,
        skew=skew,
    )


def analyze_surface_data_quality(
    points: list[VolatilityPoint],
) -> SurfaceDataQuality:
    """Detect basic duplicate and structural data-quality issues."""
    if not points:
        raise ValueError(
            "At least one volatility point is required."
        )

    keys = [
        (
            point.strike_price,
            point.time_to_expiry,
            point.option_type,
        )
        for point in points
    ]

    seen: set[tuple[float, float, str]] = set()
    duplicate_keys: list[tuple[float, float, str]] = []

    for key in keys:
        if key in seen and key not in duplicate_keys:
            duplicate_keys.append(key)

        seen.add(key)

    expirations = {
        point.time_to_expiry
        for point in points
    }

    strikes = {
        point.strike_price
        for point in points
    }

    return SurfaceDataQuality(
        point_count=len(points),
        expiration_count=len(expirations),
        strike_count=len(strikes),
        duplicate_count=len(duplicate_keys),
        duplicate_keys=duplicate_keys,
    )