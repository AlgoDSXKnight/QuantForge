from datetime import date

from app.pricing.option_chain import OptionChain
from app.pricing.option_chain_iv import OptionChainIVPoint
from app.pricing.volatility_surface import (
    VolatilityPoint,
    VolatilitySmile,
    VolatilityTermStructurePoint,
    calculate_skew,
    calculate_term_structure,
    calculate_volatility_smile,
)


def _time_to_expiry(
    timestamp: date,
    expiration: date,
) -> float:
    """Convert an expiration date into years to expiry."""
    time_to_expiry = (
        expiration - timestamp
    ).days / 365.0

    if time_to_expiry <= 0:
        raise ValueError(
            "Expiration must be after timestamp."
        )

    return time_to_expiry


def convert_iv_points_to_surface_points(
    iv_points: list[OptionChainIVPoint],
) -> list[VolatilityPoint]:
    """Convert chain IV points into volatility-surface points."""
    if not iv_points:
        raise ValueError(
            "At least one IV point is required."
        )

    return [
        VolatilityPoint(
            strike_price=point.strike,
            time_to_expiry=_time_to_expiry(
                point.timestamp,
                point.expiration,
            ),
            implied_volatility=point.implied_volatility,
            option_type=point.option_type,
        )
        for point in iv_points
    ]


def build_surface_from_option_chain(
    option_chain: OptionChain,
    iv_points: list[OptionChainIVPoint],
) -> list[VolatilityPoint]:
    """Build volatility-surface points from an option chain IV result."""
    if not iv_points:
        raise ValueError(
            "At least one IV point is required."
        )

    if option_chain.underlying_price <= 0:
        raise ValueError(
            "Underlying price must be greater than zero."
        )

    for point in iv_points:
        if point.underlying != option_chain.underlying:
            raise ValueError(
                "IV point underlying does not match option chain."
            )

        if point.timestamp != option_chain.timestamp:
            raise ValueError(
                "IV point timestamp does not match option chain."
            )

    return convert_iv_points_to_surface_points(iv_points)


def build_smile_from_option_chain(
    option_chain: OptionChain,
    iv_points: list[OptionChainIVPoint],
    expiration: date,
) -> VolatilitySmile:
    """Build a volatility smile for one expiration."""
    surface = build_surface_from_option_chain(
        option_chain=option_chain,
        iv_points=iv_points,
    )

    time_to_expiry = _time_to_expiry(
        option_chain.timestamp,
        expiration,
    )

    return calculate_volatility_smile(
        surface,
        time_to_expiry,
    )


def build_term_structure_from_option_chain(
    option_chain: OptionChain,
    iv_points: list[OptionChainIVPoint],
    strike: float,
) -> list[VolatilityTermStructurePoint]:
    """Build volatility term structure for one strike."""
    surface = build_surface_from_option_chain(
        option_chain=option_chain,
        iv_points=iv_points,
    )

    return calculate_term_structure(
        surface,
        strike,
    )


def calculate_chain_skew(
    option_chain: OptionChain,
    iv_points: list[OptionChainIVPoint],
    expiration: date,
    lower_strike: float,
    upper_strike: float,
) -> float:
    """Calculate IV skew between two strikes for one expiration."""
    surface = build_surface_from_option_chain(
        option_chain=option_chain,
        iv_points=iv_points,
    )

    time_to_expiry = _time_to_expiry(
        option_chain.timestamp,
        expiration,
    )

    return calculate_skew(
        surface,
        time_to_expiry,
        lower_strike,
        upper_strike,
    )