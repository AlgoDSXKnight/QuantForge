from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class OptionContract:
    """
    Expiration-aware option contract.

    Parameters
    ----------
    underlying:
        Underlying asset symbol.

    option_type:
        CALL or PUT.

    strike:
        Option strike price.

    expiration:
        Contract expiration date.

    volatility:
        Annualized volatility.

    risk_free_rate:
        Annualized continuously compounded risk-free rate.

    dividend_yield:
        Annualized continuously compounded dividend yield.
    """

    underlying: str
    option_type: str
    strike: float
    expiration: date
    volatility: float
    risk_free_rate: float = 0.0
    dividend_yield: float = 0.0

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

        if self.volatility <= 0:
            raise ValueError(
                "Volatility must be greater than zero."
            )

        if self.risk_free_rate <= -1:
            raise ValueError(
                "Risk-free rate must be greater than -1."
            )

        if self.dividend_yield <= -1:
            raise ValueError(
                "Dividend yield must be greater than -1."
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


def time_to_expiration(
    contract: OptionContract,
    valuation_date: date,
) -> float:
    """
    Calculate time to expiration in years.

    Returns zero when valuation_date is the expiration
    date or later.
    """

    if valuation_date >= contract.expiration:
        return 0.0

    days = (
        contract.expiration - valuation_date
    ).days

    return days / 365.0