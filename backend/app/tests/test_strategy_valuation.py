from datetime import date

import pytest

from app.pricing.option_contract import OptionContract
from app.pricing.strategy_valuation import (
    ContractPosition,
    StrategyValue,
    calculate_position_value,
    calculate_strategy_pnl,
    calculate_strategy_value,
    calculate_strategy_value_snapshot,
)


def test_long_call_position_value() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
        risk_free_rate=0.05,
    )

    position = ContractPosition(
        contract=contract,
        quantity=1,
        premium=10.0,
    )

    value = calculate_position_value(
        position=position,
        underlying_price=100.0,
        valuation_date=date(2026, 6, 30),
    )

    assert value > 0.0


def test_short_call_position_value_is_negative() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
        risk_free_rate=0.05,
    )

    position = ContractPosition(
        contract=contract,
        quantity=-1,
        premium=10.0,
    )

    value = calculate_position_value(
        position=position,
        underlying_price=100.0,
        valuation_date=date(2026, 6, 30),
    )

    assert value < 0.0


def test_strategy_value_with_multiple_positions() -> None:
    call = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
        risk_free_rate=0.05,
    )

    put = OptionContract(
        underlying="INFY",
        option_type="PUT",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
        risk_free_rate=0.05,
    )

    positions = [
        ContractPosition(
            contract=call,
            quantity=1,
            premium=10.0,
        ),
        ContractPosition(
            contract=put,
            quantity=1,
            premium=10.0,
        ),
    ]

    value = calculate_strategy_value(
        positions=positions,
        underlying_price=100.0,
        valuation_date=date(2026, 6, 30),
    )

    assert value > 0.0


def test_long_position_pnl_at_expiry() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
    )

    position = ContractPosition(
        contract=contract,
        quantity=1,
        premium=5.0,
    )

    pnl = calculate_strategy_pnl(
        positions=[position],
        underlying_price=120.0,
        valuation_date=date(2026, 12, 31),
    )

    assert pnl == 15.0


def test_short_position_pnl_at_expiry() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
    )

    position = ContractPosition(
        contract=contract,
        quantity=-1,
        premium=5.0,
    )

    pnl = calculate_strategy_pnl(
        positions=[position],
        underlying_price=120.0,
        valuation_date=date(2026, 12, 31),
    )

    assert pnl == -15.0


def test_strategy_value_snapshot() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
        risk_free_rate=0.05,
    )

    position = ContractPosition(
        contract=contract,
        quantity=1,
        premium=10.0,
    )

    snapshot = calculate_strategy_value_snapshot(
        positions=[position],
        underlying_price=110.0,
        valuation_date=date(2026, 6, 30),
    )

    assert isinstance(
        snapshot,
        StrategyValue,
    )

    assert snapshot.valuation_date == date(2026, 6, 30)
    assert snapshot.underlying_price == 110.0
    assert snapshot.market_value > 0.0


def test_requires_positions() -> None:
    with pytest.raises(
        ValueError,
        match="At least one position",
    ):
        calculate_strategy_value(
            positions=[],
            underlying_price=100.0,
            valuation_date=date(2026, 6, 30),
        )


def test_rejects_zero_quantity() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
    )

    position = ContractPosition(
        contract=contract,
        quantity=0,
        premium=5.0,
    )

    with pytest.raises(
        ValueError,
        match="quantity cannot be zero",
    ):
        calculate_position_value(
            position=position,
            underlying_price=100.0,
            valuation_date=date(2026, 6, 30),
        )


def test_rejects_negative_premium() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
    )

    position = ContractPosition(
        contract=contract,
        quantity=1,
        premium=-1.0,
    )

    with pytest.raises(
        ValueError,
        match="Premium cannot be negative",
    ):
        calculate_position_value(
            position=position,
            underlying_price=100.0,
            valuation_date=date(2026, 6, 30),
        )