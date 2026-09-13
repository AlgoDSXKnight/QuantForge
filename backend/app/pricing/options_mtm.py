from dataclasses import dataclass
from datetime import date
from typing import Sequence

from app.pricing.option_contract import OptionContract
from app.pricing.option_valuation import calculate_option_value
from app.pricing.strategy_valuation import ContractPosition


@dataclass(frozen=True)
class MTMBar:
    timestamp: date
    underlying_price: float
    volatility: float | None = None


@dataclass(frozen=True)
class MTMSnapshot:
    timestamp: date
    underlying_price: float
    volatility: float
    market_value: float
    pnl: float


def _validate_bars(
    bars: Sequence[MTMBar],
) -> None:
    if not bars:
        raise ValueError(
            "At least one MTM bar is required."
        )

    previous_timestamp: date | None = None

    for bar in bars:
        if bar.underlying_price <= 0:
            raise ValueError(
                "Underlying price must be greater than zero."
            )

        if bar.volatility is not None and bar.volatility <= 0:
            raise ValueError(
                "Volatility must be greater than zero."
            )

        if (
            previous_timestamp is not None
            and bar.timestamp <= previous_timestamp
        ):
            raise ValueError(
                "MTM bars must be strictly chronological."
            )

        previous_timestamp = bar.timestamp


def _calculate_position_market_value(
    position: ContractPosition,
    underlying_price: float,
    valuation_date: date,
    volatility: float,
) -> float:
    contract = position.contract

    contract_with_volatility = OptionContract(
        underlying=contract.underlying,
        option_type=contract.option_type,
        strike=contract.strike,
        expiration=contract.expiration,
        volatility=volatility,
        risk_free_rate=contract.risk_free_rate,
        dividend_yield=contract.dividend_yield,
    )

    option_value = calculate_option_value(
        contract=contract_with_volatility,
        underlying_price=underlying_price,
        valuation_date=valuation_date,
    )

    return option_value * position.quantity


def calculate_mtm_snapshot(
    positions: list[ContractPosition],
    bar: MTMBar,
) -> MTMSnapshot:
    if not positions:
        raise ValueError(
            "At least one position is required."
        )

    if bar.underlying_price <= 0:
        raise ValueError(
            "Underlying price must be greater than zero."
        )

    volatility = (
        bar.volatility
        if bar.volatility is not None
        else positions[0].contract.volatility
    )

    if volatility <= 0:
        raise ValueError(
            "Volatility must be greater than zero."
        )

    market_value = 0.0
    pnl = 0.0

    for position in positions:
        position_value = _calculate_position_market_value(
            position=position,
            underlying_price=bar.underlying_price,
            valuation_date=bar.timestamp,
            volatility=volatility,
        )

        market_value += position_value

        if position.quantity > 0:
            pnl += (
                position_value
                - position.premium * position.quantity
            )
        else:
            contracts_sold = abs(position.quantity)

            pnl += (
                position.premium * contracts_sold
                + position_value
            )

    return MTMSnapshot(
        timestamp=bar.timestamp,
        underlying_price=bar.underlying_price,
        volatility=volatility,
        market_value=market_value,
        pnl=pnl,
    )


def calculate_mtm_curve(
    positions: list[ContractPosition],
    bars: Sequence[MTMBar],
) -> list[MTMSnapshot]:
    if not positions:
        raise ValueError(
            "At least one position is required."
        )

    _validate_bars(bars)

    return [
        calculate_mtm_snapshot(
            positions=positions,
            bar=bar,
        )
        for bar in bars
    ]