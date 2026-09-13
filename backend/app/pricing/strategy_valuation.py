from dataclasses import dataclass
from datetime import date

from app.pricing.option_contract import OptionContract
from app.pricing.option_valuation import calculate_option_value


@dataclass(frozen=True)
class ContractPosition:
    """
    One option contract position inside a strategy.

    quantity:
        Positive for long positions.
        Negative for short positions.
    """

    contract: OptionContract
    quantity: int
    premium: float


@dataclass(frozen=True)
class StrategyValue:
    """
    Market value of an option strategy.
    """

    valuation_date: date
    underlying_price: float
    market_value: float
    pnl: float


def _validate_position(
    position: ContractPosition,
) -> None:
    if position.quantity == 0:
        raise ValueError(
            "Position quantity cannot be zero."
        )

    if position.premium < 0:
        raise ValueError(
            "Premium cannot be negative."
        )


def calculate_position_value(
    position: ContractPosition,
    underlying_price: float,
    valuation_date: date,
) -> float:
    """
    Calculate the current market value of one
    option position.
    """

    _validate_position(position)

    option_value = calculate_option_value(
        contract=position.contract,
        underlying_price=underlying_price,
        valuation_date=valuation_date,
    )

    return option_value * position.quantity


def calculate_strategy_value(
    positions: list[ContractPosition],
    underlying_price: float,
    valuation_date: date,
) -> float:
    """
    Calculate the current market value of all
    option positions in a strategy.
    """

    if not positions:
        raise ValueError(
            "At least one position is required."
        )

    return sum(
        calculate_position_value(
            position,
            underlying_price,
            valuation_date,
        )
        for position in positions
    )


def calculate_strategy_pnl(
    positions: list[ContractPosition],
    underlying_price: float,
    valuation_date: date,
) -> float:
    """
    Calculate strategy P&L relative to the original
    entry premiums.

    Long position:
        market value - premium paid

    Short position:
        premium received - market value
    """

    if not positions:
        raise ValueError(
            "At least one position is required."
        )

    pnl = 0.0

    for position in positions:
        _validate_position(position)

        market_value = calculate_position_value(
            position,
            underlying_price,
            valuation_date,
        )

        if position.quantity > 0:
            entry_cash_flow = (
                position.premium
                * position.quantity
            )

            pnl += (
                market_value
                - entry_cash_flow
            )

        else:
            contracts_sold = abs(
                position.quantity
            )

            entry_cash_flow = (
                position.premium
                * contracts_sold
            )

            pnl += (
                entry_cash_flow
                + market_value
            )

    return pnl


def calculate_strategy_value_snapshot(
    positions: list[ContractPosition],
    underlying_price: float,
    valuation_date: date,
) -> StrategyValue:
    """
    Calculate a complete strategy valuation snapshot.
    """

    market_value = calculate_strategy_value(
        positions=positions,
        underlying_price=underlying_price,
        valuation_date=valuation_date,
    )

    pnl = calculate_strategy_pnl(
        positions=positions,
        underlying_price=underlying_price,
        valuation_date=valuation_date,
    )

    return StrategyValue(
        valuation_date=valuation_date,
        underlying_price=underlying_price,
        market_value=market_value,
        pnl=pnl,
    )