from dataclasses import dataclass
from datetime import date

from app.pricing.option_chain import OptionChain
from app.pricing.option_chain_iv import OptionChainIVPoint


@dataclass(frozen=True)
class StrikeIV:
    strike: float
    call_iv: float | None
    put_iv: float | None


@dataclass(frozen=True)
class ExpirationIV:
    expiration: date
    call_iv: float | None
    put_iv: float | None


@dataclass(frozen=True)
class OptionChainAnalytics:
    underlying: str
    timestamp: date
    underlying_price: float
    atm_call_iv: float | None
    atm_put_iv: float | None
    atm_iv: float | None
    strike_iv: list[StrikeIV]
    expiration_iv: list[ExpirationIV]


def _nearest_atm_point(
    points: list[OptionChainIVPoint],
    option_type: str,
    underlying_price: float,
) -> OptionChainIVPoint | None:
    candidates = [
        point
        for point in points
        if point.option_type == option_type
    ]

    if not candidates:
        return None

    return min(
        candidates,
        key=lambda point: abs(
            point.strike - underlying_price
        ),
    )


def calculate_atm_iv(
    points: list[OptionChainIVPoint],
    underlying_price: float,
) -> tuple[float | None, float | None, float | None]:
    """Calculate nearest-ATM call IV, put IV, and combined ATM IV."""
    if underlying_price <= 0:
        raise ValueError(
            "Underlying price must be greater than zero."
        )

    call = _nearest_atm_point(
        points,
        "CALL",
        underlying_price,
    )
    put = _nearest_atm_point(
        points,
        "PUT",
        underlying_price,
    )

    call_iv = call.implied_volatility if call else None
    put_iv = put.implied_volatility if put else None

    valid_ivs = [
        value
        for value in (call_iv, put_iv)
        if value is not None
    ]

    atm_iv = (
        sum(valid_ivs) / len(valid_ivs)
        if valid_ivs
        else None
    )

    return call_iv, put_iv, atm_iv


def calculate_strike_iv(
    points: list[OptionChainIVPoint],
) -> list[StrikeIV]:
    """Group IV observations by strike."""
    strikes = sorted(
        {point.strike for point in points}
    )

    result: list[StrikeIV] = []

    for strike in strikes:
        call_values = [
            point.implied_volatility
            for point in points
            if point.strike == strike
            and point.option_type == "CALL"
        ]

        put_values = [
            point.implied_volatility
            for point in points
            if point.strike == strike
            and point.option_type == "PUT"
        ]

        result.append(
            StrikeIV(
                strike=strike,
                call_iv=(
                    sum(call_values) / len(call_values)
                    if call_values
                    else None
                ),
                put_iv=(
                    sum(put_values) / len(put_values)
                    if put_values
                    else None
                ),
            )
        )

    return result


def calculate_expiration_iv(
    points: list[OptionChainIVPoint],
) -> list[ExpirationIV]:
    """Group IV observations by expiration."""
    expirations = sorted(
        {point.expiration for point in points}
    )

    result: list[ExpirationIV] = []

    for expiration in expirations:
        call_values = [
            point.implied_volatility
            for point in points
            if point.expiration == expiration
            and point.option_type == "CALL"
        ]

        put_values = [
            point.implied_volatility
            for point in points
            if point.expiration == expiration
            and point.option_type == "PUT"
        ]

        result.append(
            ExpirationIV(
                expiration=expiration,
                call_iv=(
                    sum(call_values) / len(call_values)
                    if call_values
                    else None
                ),
                put_iv=(
                    sum(put_values) / len(put_values)
                    if put_values
                    else None
                ),
            )
        )

    return result


def build_option_chain_analytics(
    option_chain: OptionChain,
    iv_points: list[OptionChainIVPoint],
) -> OptionChainAnalytics:
    """Build chain-level IV analytics from an option chain."""
    if not iv_points:
        raise ValueError(
            "At least one IV point is required."
        )

    if option_chain.underlying_price <= 0:
        raise ValueError(
            "Underlying price must be greater than zero."
        )

    atm_call_iv, atm_put_iv, atm_iv = calculate_atm_iv(
        points=iv_points,
        underlying_price=option_chain.underlying_price,
    )

    return OptionChainAnalytics(
        underlying=option_chain.underlying,
        timestamp=option_chain.timestamp,
        underlying_price=option_chain.underlying_price,
        atm_call_iv=atm_call_iv,
        atm_put_iv=atm_put_iv,
        atm_iv=atm_iv,
        strike_iv=calculate_strike_iv(iv_points),
        expiration_iv=calculate_expiration_iv(iv_points),
    )


def calculate_call_put_iv_difference(
    analytics: OptionChainAnalytics,
) -> float | None:
    """Return ATM call IV minus ATM put IV."""
    if (
        analytics.atm_call_iv is None
        or analytics.atm_put_iv is None
    ):
        return None

    return (
        analytics.atm_call_iv
        - analytics.atm_put_iv
    )


def calculate_strike_skew(
    analytics: OptionChainAnalytics,
    lower_strike: float,
    upper_strike: float,
    option_type: str = "CALL",
) -> float:
    """Calculate IV difference between two strikes."""
    if lower_strike >= upper_strike:
        raise ValueError(
            "Lower strike must be less than upper strike."
        )

    normalized_type = option_type.strip().upper()

    if normalized_type not in {"CALL", "PUT"}:
        raise ValueError(
            "Option type must be CALL or PUT."
        )

    lower = next(
        (
            item
            for item in analytics.strike_iv
            if item.strike == lower_strike
        ),
        None,
    )

    upper = next(
        (
            item
            for item in analytics.strike_iv
            if item.strike == upper_strike
        ),
        None,
    )

    if lower is None or upper is None:
        raise ValueError(
            "Both strikes must exist in the analytics."
        )

    lower_iv = (
        lower.call_iv
        if normalized_type == "CALL"
        else lower.put_iv
    )
    upper_iv = (
        upper.call_iv
        if normalized_type == "CALL"
        else upper.put_iv
    )

    if lower_iv is None or upper_iv is None:
        raise ValueError(
            "Both strikes must contain the requested option type."
        )

    return upper_iv - lower_iv