from datetime import date

import pytest

from app.pricing.option_chain import OptionChain
from app.pricing.option_market_data import OptionMarketData


TIMESTAMP = date(2026, 6, 1)
EXPIRATION = date(2026, 6, 25)


def create_option(
    option_type: str,
    strike: float,
) -> OptionMarketData:
    return OptionMarketData(
        underlying="INFY",
        timestamp=TIMESTAMP,
        option_type=option_type,
        strike=strike,
        expiration=EXPIRATION,
        bid=80.0,
        ask=90.0,
        last_price=85.0,
        underlying_price=1900.0,
    )


def create_chain() -> OptionChain:
    return OptionChain(
        underlying="INFY",
        timestamp=TIMESTAMP,
        underlying_price=1900.0,
        options=[
            create_option("CALL", 1800.0),
            create_option("CALL", 1900.0),
            create_option("CALL", 2000.0),
            create_option("PUT", 1800.0),
            create_option("PUT", 1900.0),
            create_option("PUT", 2000.0),
        ],
    )


def test_create_option_chain() -> None:
    chain = create_chain()

    assert chain.underlying == "INFY"
    assert chain.underlying_price == 1900.0
    assert len(chain.options) == 6


def test_filter_by_expiration() -> None:
    chain = create_chain()

    result = chain.filter_by_expiration(
        EXPIRATION
    )

    assert len(result) == 6


def test_filter_by_option_type() -> None:
    chain = create_chain()

    calls = chain.filter_by_option_type("CALL")
    puts = chain.filter_by_option_type("PUT")

    assert len(calls) == 3
    assert len(puts) == 3


def test_filter_by_strike() -> None:
    chain = create_chain()

    result = chain.filter_by_strike(1900.0)

    assert len(result) == 2


def test_expirations() -> None:
    chain = create_chain()

    assert chain.expirations() == [
        EXPIRATION
    ]


def test_strikes() -> None:
    chain = create_chain()

    assert chain.strikes() == [
        1800.0,
        1900.0,
        2000.0,
    ]


def test_calls_and_puts() -> None:
    chain = create_chain()

    assert len(chain.calls()) == 3
    assert len(chain.puts()) == 3


def test_nearest_atm_call() -> None:
    chain = create_chain()

    option = chain.nearest_atm("CALL")

    assert option is not None
    assert option.strike == 1900.0


def test_nearest_atm_put() -> None:
    chain = create_chain()

    option = chain.nearest_atm("PUT")

    assert option is not None
    assert option.strike == 1900.0


def test_nearest_atm_returns_none_when_empty() -> None:
    chain = OptionChain(
        underlying="INFY",
        timestamp=TIMESTAMP,
        underlying_price=1900.0,
        options=[],
    )

    assert chain.nearest_atm("CALL") is None


def test_rejects_invalid_option_type() -> None:
    chain = create_chain()

    with pytest.raises(
        ValueError,
        match="Option type",
    ):
        chain.filter_by_option_type("WRONG")


def test_rejects_mismatched_underlying() -> None:
    option = OptionMarketData(
        underlying="TCS",
        timestamp=TIMESTAMP,
        option_type="CALL",
        strike=1900.0,
        expiration=EXPIRATION,
        bid=80.0,
        ask=90.0,
        last_price=85.0,
        underlying_price=1900.0,
    )

    with pytest.raises(
        ValueError,
        match="same underlying",
    ):
        OptionChain(
            underlying="INFY",
            timestamp=TIMESTAMP,
            underlying_price=1900.0,
            options=[option],
        )