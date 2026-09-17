from dataclasses import dataclass
from datetime import date

from app.pricing.implied_volatility import implied_volatility
from app.pricing.option_chain import OptionChain
from app.pricing.option_market_data import OptionMarketData


@dataclass(frozen=True)
class OptionChainIVPoint:
    underlying: str
    timestamp: date
    option_type: str
    strike: float
    expiration: date
    option_price: float
    underlying_price: float
    implied_volatility: float


@dataclass(frozen=True)
class OptionChainIVResult:
    points: list[OptionChainIVPoint]
    failed_contracts: int


def calculate_option_iv(
    option: OptionMarketData,
    risk_free_rate: float,
) -> float:
    """Calculate implied volatility for a single option quote."""
    time_to_expiry = (
        option.expiration - option.timestamp
    ).days / 365.0

    if time_to_expiry <= 0:
        raise ValueError(
            "Option must have positive time to expiry."
        )

    if risk_free_rate < -1.0:
        raise ValueError(
            "Risk-free rate must be greater than or equal to -1."
        )

    return implied_volatility(
        spot_price=option.underlying_price,
        strike_price=option.strike,
        time_to_expiry=time_to_expiry,
        risk_free_rate=risk_free_rate,
        option_price=option.mid_price,
        option_type=option.option_type,
    )


def calculate_option_chain_iv(
    option_chain: OptionChain,
    risk_free_rate: float,
) -> OptionChainIVResult:
    """Calculate implied volatility for every usable option in a chain."""
    if risk_free_rate < -1.0:
        raise ValueError(
            "Risk-free rate must be greater than or equal to -1."
        )

    points: list[OptionChainIVPoint] = []
    failed_contracts = 0

    for option in option_chain.options:
        try:
            volatility = calculate_option_iv(
                option=option,
                risk_free_rate=risk_free_rate,
            )
        except (ValueError, ZeroDivisionError):
            failed_contracts += 1
            continue

        points.append(
            OptionChainIVPoint(
                underlying=option.underlying,
                timestamp=option.timestamp,
                option_type=option.option_type,
                strike=option.strike,
                expiration=option.expiration,
                option_price=option.mid_price,
                underlying_price=option.underlying_price,
                implied_volatility=volatility,
            )
        )

    if not points:
        raise ValueError(
            "No option contracts produced a valid implied volatility."
        )

    return OptionChainIVResult(
        points=points,
        failed_contracts=failed_contracts,
    )


def average_chain_iv(result: OptionChainIVResult) -> float:
    """Return the arithmetic mean IV across valid option contracts."""
    if not result.points:
        raise ValueError("Cannot calculate average IV without points.")

    return sum(
        point.implied_volatility
        for point in result.points
    ) / len(result.points)


def filter_chain_iv_by_expiration(
    result: OptionChainIVResult,
    expiration: date,
) -> list[OptionChainIVPoint]:
    """Return IV points for a specific expiration."""
    return [
        point
        for point in result.points
        if point.expiration == expiration
    ]


def filter_chain_iv_by_option_type(
    result: OptionChainIVResult,
    option_type: str,
) -> list[OptionChainIVPoint]:
    """Return IV points for CALL or PUT contracts."""
    normalized_type = option_type.strip().upper()

    if normalized_type not in {"CALL", "PUT"}:
        raise ValueError(
            "Option type must be CALL or PUT."
        )

    return [
        point
        for point in result.points
        if point.option_type == normalized_type
    ]