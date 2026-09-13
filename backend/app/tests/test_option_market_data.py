from datetime import date

import pytest

from app.pricing.option_market_data import (
    OptionMarketData,
)


def create_option_quote() -> OptionMarketData:
    return OptionMarketData(
        underlying="INFY",
        timestamp=date(2026, 6, 1),
        option_type="CALL",
        strike=1900.0,
        expiration=date(2026, 6, 25),
        bid=82.0,
        ask=86.0,
        last_price=84.0,
        underlying_price=1920.0,
    )


def test_create_option_market_data() -> None:
    quote = create_option_quote()

    assert quote.underlying == "INFY"
    assert quote.option_type == "CALL"
    assert quote.strike == 1900.0
    assert quote.bid == 82.0
    assert quote.ask == 86.0
    assert quote.last_price == 84.0
    assert quote.underlying_price == 1920.0


def test_normalizes_symbol_and_option_type() -> None:
    quote = OptionMarketData(
        underlying=" infy ",
        timestamp=date(2026, 6, 1),
        option_type=" call ",
        strike=1900.0,
        expiration=date(2026, 6, 25),
        bid=82.0,
        ask=86.0,
        last_price=84.0,
        underlying_price=1920.0,
    )

    assert quote.underlying == "INFY"
    assert quote.option_type == "CALL"


def test_mid_price() -> None:
    quote = create_option_quote()

    assert quote.mid_price == 84.0


def test_mid_price_with_uneven_bid_ask() -> None:
    quote = OptionMarketData(
        underlying="INFY",
        timestamp=date(2026, 6, 1),
        option_type="PUT",
        strike=1900.0,
        expiration=date(2026, 6, 25),
        bid=75.0,
        ask=81.0,
        last_price=78.0,
        underlying_price=1920.0,
    )

    assert quote.mid_price == 78.0


def test_rejects_empty_underlying() -> None:
    with pytest.raises(
        ValueError,
        match="Underlying symbol",
    ):
        OptionMarketData(
            underlying=" ",
            timestamp=date(2026, 6, 1),
            option_type="CALL",
            strike=1900.0,
            expiration=date(2026, 6, 25),
            bid=82.0,
            ask=86.0,
            last_price=84.0,
            underlying_price=1920.0,
        )


def test_rejects_invalid_option_type() -> None:
    with pytest.raises(
        ValueError,
        match="Option type",
    ):
        OptionMarketData(
            underlying="INFY",
            timestamp=date(2026, 6, 1),
            option_type="WRONG",
            strike=1900.0,
            expiration=date(2026, 6, 25),
            bid=82.0,
            ask=86.0,
            last_price=84.0,
            underlying_price=1920.0,
        )


def test_rejects_invalid_strike() -> None:
    with pytest.raises(
        ValueError,
        match="Strike",
    ):
        OptionMarketData(
            underlying="INFY",
            timestamp=date(2026, 6, 1),
            option_type="CALL",
            strike=0.0,
            expiration=date(2026, 6, 25),
            bid=82.0,
            ask=86.0,
            last_price=84.0,
            underlying_price=1920.0,
        )


def test_rejects_expiration_on_quote_date() -> None:
    with pytest.raises(
        ValueError,
        match="Expiration",
    ):
        OptionMarketData(
            underlying="INFY",
            timestamp=date(2026, 6, 25),
            option_type="CALL",
            strike=1900.0,
            expiration=date(2026, 6, 25),
            bid=82.0,
            ask=86.0,
            last_price=84.0,
            underlying_price=1920.0,
        )


def test_rejects_negative_bid() -> None:
    with pytest.raises(
        ValueError,
        match="Bid",
    ):
        OptionMarketData(
            underlying="INFY",
            timestamp=date(2026, 6, 1),
            option_type="CALL",
            strike=1900.0,
            expiration=date(2026, 6, 25),
            bid=-1.0,
            ask=86.0,
            last_price=84.0,
            underlying_price=1920.0,
        )


def test_rejects_negative_ask() -> None:
    with pytest.raises(
        ValueError,
        match="Ask",
    ):
        OptionMarketData(
            underlying="INFY",
            timestamp=date(2026, 6, 1),
            option_type="CALL",
            strike=1900.0,
            expiration=date(2026, 6, 25),
            bid=82.0,
            ask=-1.0,
            last_price=84.0,
            underlying_price=1920.0,
        )


def test_rejects_ask_below_bid() -> None:
    with pytest.raises(
        ValueError,
        match="Ask price cannot be lower",
    ):
        OptionMarketData(
            underlying="INFY",
            timestamp=date(2026, 6, 1),
            option_type="CALL",
            strike=1900.0,
            expiration=date(2026, 6, 25),
            bid=90.0,
            ask=80.0,
            last_price=84.0,
            underlying_price=1920.0,
        )


def test_rejects_negative_last_price() -> None:
    with pytest.raises(
        ValueError,
        match="Last price",
    ):
        OptionMarketData(
            underlying="INFY",
            timestamp=date(2026, 6, 1),
            option_type="CALL",
            strike=1900.0,
            expiration=date(2026, 6, 25),
            bid=82.0,
            ask=86.0,
            last_price=-1.0,
            underlying_price=1920.0,
        )


def test_rejects_invalid_underlying_price() -> None:
    with pytest.raises(
        ValueError,
        match="Underlying price",
    ):
        OptionMarketData(
            underlying="INFY",
            timestamp=date(2026, 6, 1),
            option_type="CALL",
            strike=1900.0,
            expiration=date(2026, 6, 25),
            bid=82.0,
            ask=86.0,
            last_price=84.0,
            underlying_price=0.0,
        )


def test_put_quote() -> None:
    quote = OptionMarketData(
        underlying="TCS",
        timestamp=date(2026, 6, 1),
        option_type="PUT",
        strike=3500.0,
        expiration=date(2026, 6, 25),
        bid=120.0,
        ask=130.0,
        last_price=125.0,
        underlying_price=3520.0,
    )

    assert quote.option_type == "PUT"
    assert quote.mid_price == 125.0