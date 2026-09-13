from datetime import date

from app.pricing.black_scholes import (
    black_scholes_call,
    black_scholes_put,
)
from app.pricing.option_contract import (
    OptionContract,
    time_to_expiration,
)


def calculate_option_value(
    contract: OptionContract,
    underlying_price: float,
    valuation_date: date,
) -> float:
    """
    Calculate the theoretical value of an option contract
    on a specific valuation date.

    Black-Scholes is used while time remains until expiry.

    At expiry or after expiry, intrinsic value is returned.
    """

    if underlying_price <= 0:
        raise ValueError(
            "Underlying price must be greater than zero."
        )

    time_remaining = time_to_expiration(
        contract,
        valuation_date,
    )

    if time_remaining == 0.0:
        if contract.option_type == "CALL":
            return max(
                underlying_price - contract.strike,
                0.0,
            )

        return max(
            contract.strike - underlying_price,
            0.0,
        )

    if contract.option_type == "CALL":
        return black_scholes_call(
            spot_price=underlying_price,
            strike_price=contract.strike,
            time_to_expiry=time_remaining,
            risk_free_rate=contract.risk_free_rate,
            volatility=contract.volatility,
        )

    return black_scholes_put(
        spot_price=underlying_price,
        strike_price=contract.strike,
        time_to_expiry=time_remaining,
        risk_free_rate=contract.risk_free_rate,
        volatility=contract.volatility,
    )