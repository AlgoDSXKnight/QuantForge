from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class OptionMarketData:
    """
    Historical market quote for one option contract.
    """

    underlying: str
    timestamp: date
    option_type: str
    strike: float
    expiration: date

    bid: float
    ask: float
    last_price: float

    underlying_price: float

    def __post_init__(self) -> None:
        underlying = self.underlying.strip().upper()
        option_type = self.option_type.strip().upper()

        if not underlying:
            raise ValueError(
                "Underlying symbol cannot be empty."
            )

        if option_type not in {"CALL", "PUT"}:
            raise ValueError(
                "Option type must be CALL or PUT."
            )

        if self.strike <= 0:
            raise ValueError(
                "Strike price must be greater than zero."
            )

        if self.expiration <= self.timestamp:
            raise ValueError(
                "Expiration must be after quote timestamp."
            )

        if self.bid < 0:
            raise ValueError(
                "Bid price cannot be negative."
            )

        if self.ask < 0:
            raise ValueError(
                "Ask price cannot be negative."
            )

        if self.ask < self.bid:
            raise ValueError(
                "Ask price cannot be lower than bid price."
            )

        if self.last_price < 0:
            raise ValueError(
                "Last price cannot be negative."
            )

        if self.underlying_price <= 0:
            raise ValueError(
                "Underlying price must be greater than zero."
            )

        object.__setattr__(
            self,
            "underlying",
            underlying,
        )

        object.__setattr__(
            self,
            "option_type",
            option_type,
        )

    @property
    def mid_price(self) -> float:
        """
        Mid-market price between bid and ask.
        """
        return (
            self.bid + self.ask
        ) / 2.0