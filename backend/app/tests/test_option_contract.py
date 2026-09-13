from datetime import date

import pytest

from app.pricing.option_contract import (
    OptionContract,
    time_to_expiration,
)


def test_create_call_contract() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=2000.0,
        expiration=date(2026, 12, 31),
        volatility=0.25,
        risk_free_rate=0.06,
        dividend_yield=0.01,
    )

    assert contract.underlying == "INFY"
    assert contract.option_type == "CALL"
    assert contract.strike == 2000.0
    assert contract.expiration == date(2026, 12, 31)
    assert contract.volatility == 0.25
    assert contract.risk_free_rate == 0.06
    assert contract.dividend_yield == 0.01


def test_symbol_and_option_type_are_normalized() -> None:
    contract = OptionContract(
        underlying=" infy ",
        option_type=" call ",
        strike=2000.0,
        expiration=date(2026, 12, 31),
        volatility=0.25,
    )

    assert contract.underlying == "INFY"
    assert contract.option_type == "CALL"


def test_put_contract() -> None:
    contract = OptionContract(
        underlying="TCS",
        option_type="PUT",
        strike=3500.0,
        expiration=date(2026, 12, 31),
        volatility=0.30,
    )

    assert contract.option_type == "PUT"


def test_rejects_empty_underlying() -> None:
    with pytest.raises(
        ValueError,
        match="Underlying symbol",
    ):
        OptionContract(
            underlying="",
            option_type="CALL",
            strike=100.0,
            expiration=date(2026, 12, 31),
            volatility=0.20,
        )


def test_rejects_invalid_option_type() -> None:
    with pytest.raises(
        ValueError,
        match="Option type",
    ):
        OptionContract(
            underlying="INFY",
            option_type="INVALID",
            strike=100.0,
            expiration=date(2026, 12, 31),
            volatility=0.20,
        )


def test_rejects_invalid_strike() -> None:
    with pytest.raises(
        ValueError,
        match="Strike price",
    ):
        OptionContract(
            underlying="INFY",
            option_type="CALL",
            strike=0.0,
            expiration=date(2026, 12, 31),
            volatility=0.20,
        )


def test_rejects_invalid_volatility() -> None:
    with pytest.raises(
        ValueError,
        match="Volatility",
    ):
        OptionContract(
            underlying="INFY",
            option_type="CALL",
            strike=100.0,
            expiration=date(2026, 12, 31),
            volatility=0.0,
        )


def test_rejects_invalid_risk_free_rate() -> None:
    with pytest.raises(
        ValueError,
        match="Risk-free rate",
    ):
        OptionContract(
            underlying="INFY",
            option_type="CALL",
            strike=100.0,
            expiration=date(2026, 12, 31),
            volatility=0.20,
            risk_free_rate=-1.0,
        )


def test_rejects_invalid_dividend_yield() -> None:
    with pytest.raises(
        ValueError,
        match="Dividend yield",
    ):
        OptionContract(
            underlying="INFY",
            option_type="CALL",
            strike=100.0,
            expiration=date(2026, 12, 31),
            volatility=0.20,
            dividend_yield=-1.0,
        )


def test_time_to_expiration() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=2000.0,
        expiration=date(2026, 12, 31),
        volatility=0.25,
    )

    valuation_date = date(2026, 7, 1)

    result = time_to_expiration(
        contract,
        valuation_date,
    )

    expected_days = (
        date(2026, 12, 31)
        - valuation_date
    ).days

    assert result == pytest.approx(
        expected_days / 365.0,
    )


def test_time_to_expiration_on_expiry() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=2000.0,
        expiration=date(2026, 12, 31),
        volatility=0.25,
    )

    assert (
        time_to_expiration(
            contract,
            date(2026, 12, 31),
        )
        == 0.0
    )


def test_time_to_expiration_after_expiry() -> None:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=2000.0,
        expiration=date(2026, 12, 31),
        volatility=0.25,
    )

    assert (
        time_to_expiration(
            contract,
            date(2027, 1, 1),
        )
        == 0.0
    )