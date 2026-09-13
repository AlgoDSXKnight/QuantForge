from dataclasses import dataclass
from datetime import date

from app.pricing.implied_volatility import (
    implied_volatility,
)
from app.pricing.option_market_data import (
    OptionMarketData,
)


@dataclass(frozen=True)
class HistoricalIVPoint:
    """
    Historical implied-volatility observation.
    """

    underlying: str
    timestamp: date
    option_type: str
    strike: float
    expiration: date
    underlying_price: float
    option_price: float
    implied_volatility: float


def calculate_historical_iv(
    market_data: OptionMarketData,
    risk_free_rate: float = 0.0,
) -> HistoricalIVPoint:
    """
    Calculate implied volatility from an observed
    option market quote.

    The midpoint of bid/ask is used as the
    market option price.
    """

    if risk_free_rate <= -1:
        raise ValueError(
            "Risk-free rate must be greater than -1."
        )

    time_to_expiry = (
        market_data.expiration
        - market_data.timestamp
    ).days / 365.0

    if time_to_expiry <= 0:
        raise ValueError(
            "Time to expiry must be greater than zero."
        )

    option_price = market_data.mid_price

    iv = implied_volatility(
        spot_price=market_data.underlying_price,
        strike_price=market_data.strike,
        time_to_expiry=time_to_expiry,
        risk_free_rate=risk_free_rate,
        option_price=option_price,
        option_type=market_data.option_type,
    )

    return HistoricalIVPoint(
        underlying=market_data.underlying,
        timestamp=market_data.timestamp,
        option_type=market_data.option_type,
        strike=market_data.strike,
        expiration=market_data.expiration,
        underlying_price=market_data.underlying_price,
        option_price=option_price,
        implied_volatility=iv,
    )