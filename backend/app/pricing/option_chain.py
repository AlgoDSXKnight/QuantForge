from dataclasses import dataclass
from datetime import date

from app.pricing.option_market_data import OptionMarketData


@dataclass(frozen=True)
class OptionChain:
    underlying: str
    timestamp: date
    underlying_price: float
    options: list[OptionMarketData]

    def __post_init__(self) -> None:
        underlying = self.underlying.strip().upper()

        if not underlying:
            raise ValueError(
                "Underlying symbol cannot be empty."
            )

        if self.underlying_price <= 0:
            raise ValueError(
                "Underlying price must be greater than zero."
            )

        for option in self.options:
            if option.underlying != underlying:
                raise ValueError(
                    "All options must belong to the same underlying."
                )

            if option.timestamp != self.timestamp:
                raise ValueError(
                    "All options must have the same timestamp."
                )

        object.__setattr__(
            self,
            "underlying",
            underlying,
        )

    def filter_by_expiration(
        self,
        expiration: date,
    ) -> list[OptionMarketData]:
        return [
            option
            for option in self.options
            if option.expiration == expiration
        ]

    def filter_by_option_type(
        self,
        option_type: str,
    ) -> list[OptionMarketData]:
        option_type = option_type.strip().upper()

        if option_type not in {"CALL", "PUT"}:
            raise ValueError(
                "Option type must be CALL or PUT."
            )

        return [
            option
            for option in self.options
            if option.option_type == option_type
        ]

    def filter_by_strike(
        self,
        strike: float,
    ) -> list[OptionMarketData]:
        if strike <= 0:
            raise ValueError(
                "Strike price must be greater than zero."
            )

        return [
            option
            for option in self.options
            if option.strike == strike
        ]

    def expirations(self) -> list[date]:
        return sorted(
            {
                option.expiration
                for option in self.options
            }
        )

    def strikes(self) -> list[float]:
        return sorted(
            {
                option.strike
                for option in self.options
            }
        )

    def calls(self) -> list[OptionMarketData]:
        return self.filter_by_option_type("CALL")

    def puts(self) -> list[OptionMarketData]:
        return self.filter_by_option_type("PUT")

    def nearest_atm(
        self,
        option_type: str,
    ) -> OptionMarketData | None:
        options = self.filter_by_option_type(
            option_type
        )

        if not options:
            return None

        return min(
            options,
            key=lambda option: abs(
                option.strike
                - self.underlying_price
            ),
        )