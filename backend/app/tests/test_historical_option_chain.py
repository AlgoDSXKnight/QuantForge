from datetime import date

import pytest

from app.pricing.historical_option_chain import (
    HistoricalOptionChainRow,
    build_option_chain,
)


TIMESTAMP = date(2026, 6, 1)
EXPIRATION = date(2026, 6, 25)


def create_row(
    option_type: str,
    strike: float,
) -> HistoricalOptionChainRow:
    return HistoricalOptionChainRow(
        underlying="INFY",
        timestamp=TIMESTAMP,
        underlying_price=1900.0,
        option_type=option_type,
        strike=strike,
        expiration=EXPIRATION,
        bid=80.0,
        ask=90.0,
        last_price=85.0,
    )


def create_rows() -> list[HistoricalOptionChainRow]:
    return [
        create_row("CALL", 1800.0),
        create_row("CALL", 1900.0),
        create_row("CALL", 2000.0),
        create_row("PUT", 1800.0),
        create_row("PUT", 1900.0),
        create_row("PUT", 2000.0),
    ]


def test_build_option_chain() -> None:
    chain = build_option_chain(create_rows())

    assert chain.underlying == "INFY"
    assert chain.timestamp == TIMESTAMP
    assert chain.underlying_price == 1900.0
    assert len(chain.options) == 6


def test_build_option_chain_creates_calls_and_puts() -> None:
    chain = build_option_chain(create_rows())

    assert len(chain.calls()) == 3
    assert len(chain.puts()) == 3


def test_build_option_chain_preserves_strikes() -> None:
    chain = build_option_chain(create_rows())

    assert chain.strikes() == [
        1800.0,
        1900.0,
        2000.0,
    ]


def test_build_option_chain_preserves_expiration() -> None:
    chain = build_option_chain(create_rows())

    assert chain.expirations() == [
        EXPIRATION
    ]


def test_build_option_chain_normalizes_underlying() -> None:
    rows = [
        HistoricalOptionChainRow(
            underlying=" infy ",
            timestamp=TIMESTAMP,
            underlying_price=1900.0,
            option_type=" call ",
            strike=1900.0,
            expiration=EXPIRATION,
            bid=80.0,
            ask=90.0,
            last_price=85.0,
        )
    ]

    chain = build_option_chain(rows)

    assert chain.underlying == "INFY"
    assert chain.options[0].underlying == "INFY"
    assert chain.options[0].option_type == "CALL"


def test_build_option_chain_requires_rows() -> None:
    with pytest.raises(
        ValueError,
        match="At least one historical option-chain row",
    ):
        build_option_chain([])


def test_build_option_chain_rejects_mismatched_underlying() -> None:
    rows = create_rows()

    rows[1] = HistoricalOptionChainRow(
        underlying="TCS",
        timestamp=TIMESTAMP,
        underlying_price=1900.0,
        option_type="CALL",
        strike=1900.0,
        expiration=EXPIRATION,
        bid=80.0,
        ask=90.0,
        last_price=85.0,
    )

    with pytest.raises(
        ValueError,
        match="same underlying",
    ):
        build_option_chain(rows)


def test_build_option_chain_rejects_mismatched_timestamp() -> None:
    rows = create_rows()

    rows[1] = HistoricalOptionChainRow(
        underlying="INFY",
        timestamp=date(2026, 6, 2),
        underlying_price=1900.0,
        option_type="CALL",
        strike=1900.0,
        expiration=EXPIRATION,
        bid=80.0,
        ask=90.0,
        last_price=85.0,
    )

    with pytest.raises(
        ValueError,
        match="same timestamp",
    ):
        build_option_chain(rows)


def test_build_option_chain_rejects_invalid_option_data() -> None:
    rows = create_rows()

    rows[0] = HistoricalOptionChainRow(
        underlying="INFY",
        timestamp=TIMESTAMP,
        underlying_price=1900.0,
        option_type="CALL",
        strike=1800.0,
        expiration=EXPIRATION,
        bid=100.0,
        ask=90.0,
        last_price=95.0,
    )

    with pytest.raises(
        ValueError,
        match="Ask price cannot be lower than bid price",
    ):
        build_option_chain(rows)