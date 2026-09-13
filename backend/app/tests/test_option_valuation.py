from datetime import date

import pytest

from app.pricing.option_contract import OptionContract
from app.pricing.option_valuation import (
    calculate_option_value,
)


def test_call_value_before_expiry() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
        risk_free_rate=0.05,
    )

    value = calculate_option_value(
        contract=contract,
        underlying_price=100.0,
        valuation_date=date(2026, 6, 30),
    )

    assert value > 0.0


def test_put_value_before_expiry() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="PUT",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
        risk_free_rate=0.05,
    )

    value = calculate_option_value(
        contract=contract,
        underlying_price=100.0,
        valuation_date=date(2026, 6, 30),
    )

    assert value > 0.0


def test_call_at_expiry_returns_intrinsic_value() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
    )

    value = calculate_option_value(
        contract=contract,
        underlying_price=120.0,
        valuation_date=date(2026, 12, 31),
    )

    assert value == 20.0


def test_put_at_expiry_returns_intrinsic_value() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="PUT",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
    )

    value = calculate_option_value(
        contract=contract,
        underlying_price=80.0,
        valuation_date=date(2026, 12, 31),
    )

    assert value == 20.0


def test_call_after_expiry_returns_intrinsic_value() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
    )

    value = calculate_option_value(
        contract=contract,
        underlying_price=120.0,
        valuation_date=date(2027, 1, 10),
    )

    assert value == 20.0


def test_put_after_expiry_returns_intrinsic_value() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="PUT",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
    )

    value = calculate_option_value(
        contract=contract,
        underlying_price=80.0,
        valuation_date=date(2027, 1, 10),
    )

    assert value == 20.0


def test_call_out_of_money_at_expiry() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
    )

    value = calculate_option_value(
        contract=contract,
        underlying_price=90.0,
        valuation_date=date(2026, 12, 31),
    )

    assert value == 0.0


def test_put_out_of_money_at_expiry() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="PUT",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
    )

    value = calculate_option_value(
        contract=contract,
        underlying_price=110.0,
        valuation_date=date(2026, 12, 31),
    )

    assert value == 0.0


def test_rejects_invalid_underlying_price() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
    )

    with pytest.raises(
        ValueError,
        match="Underlying price",
    ):
        calculate_option_value(
            contract=contract,
            underlying_price=0.0,
            valuation_date=date(2026, 6, 30),
        )