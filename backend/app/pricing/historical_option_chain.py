from dataclasses import dataclass
from datetime import date
from typing import Sequence

from app.pricing.option_chain import OptionChain
from app.pricing.option_market_data import OptionMarketData


@dataclass(frozen=True)
class HistoricalOptionChainRow:
    underlying: str
    timestamp: date
    underlying_price: float
    option_type: str
    strike: float
    expiration: date
    bid: float
    ask: float
    last_price: float


def build_option_chain(
    rows: Sequence[HistoricalOptionChainRow],
) -> OptionChain:
    if not rows:
        raise ValueError(
            "At least one historical option-chain row is required."
        )

    first_row = rows[0]

    underlying = first_row.underlying.strip().upper()

    if not underlying:
        raise ValueError(
            "Underlying symbol cannot be empty."
        )

    if first_row.underlying_price <= 0:
        raise ValueError(
            "Underlying price must be greater than zero."
        )

    options = [
        OptionMarketData(
            underlying=row.underlying,
            timestamp=row.timestamp,
            option_type=row.option_type,
            strike=row.strike,
            expiration=row.expiration,
            bid=row.bid,
            ask=row.ask,
            last_price=row.last_price,
            underlying_price=row.underlying_price,
        )
        for row in rows
    ]

    return OptionChain(
        underlying=underlying,
        timestamp=first_row.timestamp,
        underlying_price=first_row.underlying_price,
        options=options,
    )