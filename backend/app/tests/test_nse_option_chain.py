from datetime import date

import pytest

from app.market_data.nse_option_chain import (
    parse_nse_option_row,
    parse_nse_option_rows,
)


def create_row() -> dict[str, object]:
    return {
        "underlying": "INFY",
        "timestamp": "01-Jun-2026",
        "underlying_price": 1900.0,
        "option_type": "CE",
        "strike": 1900.0,
        "expiration": "25-Jun-2026",
        "bid": 80.0,
        "ask": 90.0,
        "last_price": 85.0,
    }


def test_parse_nse_option_row() -> None:
    row = create_row()

    result = parse_nse_option_row(row)

    assert result.underlying == "INFY"
    assert result.timestamp == date(2026, 6, 1)
    assert result.underlying_price == 1900.0
    assert result.option_type == "CALL"
    assert result.strike == 1900.0
    assert result.expiration == date(2026, 6, 25)
    assert result.bid == 80.0
    assert result.ask == 90.0
    assert result.last_price == 85.0


def test_parse_nse_put() -> None:
    row = create_row()
    row["option_type"] = "PE"

    result = parse_nse_option_row(row)

    assert result.option_type == "PUT"


def test_parse_call_keyword() -> None:
    row = create_row()
    row["option_type"] = "CALL"

    result = parse_nse_option_row(row)

    assert result.option_type == "CALL"


def test_parse_put_keyword() -> None:
    row = create_row()
    row["option_type"] = "PUT"

    result = parse_nse_option_row(row)

    assert result.option_type == "PUT"


def test_parse_rows() -> None:
    call = create_row()

    put = create_row()
    put["option_type"] = "PE"
    put["strike"] = 1900.0

    result = parse_nse_option_rows(
        [call, put]
    )

    assert len(result) == 2
    assert result[0].option_type == "CALL"
    assert result[1].option_type == "PUT"


def test_parse_date_formats() -> None:
    row = create_row()

    row["timestamp"] = "2026-06-01"
    row["expiration"] = "25/06/2026"

    result = parse_nse_option_row(row)

    assert result.timestamp == date(2026, 6, 1)
    assert result.expiration == date(2026, 6, 25)


def test_numeric_strings_are_parsed() -> None:
    row = create_row()

    row["underlying_price"] = "1900.50"
    row["strike"] = "1900"
    row["bid"] = "80.25"
    row["ask"] = "90.50"
    row["last_price"] = "85.75"

    result = parse_nse_option_row(row)

    assert result.underlying_price == 1900.50
    assert result.strike == 1900.0
    assert result.bid == 80.25
    assert result.ask == 90.50
    assert result.last_price == 85.75


def test_rejects_unsupported_option_type() -> None:
    row = create_row()
    row["option_type"] = "XX"

    with pytest.raises(
        ValueError,
        match="Unsupported NSE option type",
    ):
        parse_nse_option_row(row)


def test_rejects_invalid_date() -> None:
    row = create_row()
    row["timestamp"] = "invalid-date"

    with pytest.raises(
        ValueError,
        match="Unsupported date format",
    ):
        parse_nse_option_row(row)


def test_rejects_invalid_numeric_value() -> None:
    row = create_row()
    row["strike"] = "not-a-number"

    with pytest.raises(
        ValueError,
        match="strike must be numeric",
    ):
        parse_nse_option_row(row)


def test_rejects_empty_rows() -> None:
    with pytest.raises(
        ValueError,
        match="At least one NSE option row",
    ):
        parse_nse_option_rows([])


def test_preserves_underlying_normalization_downstream() -> None:
    row = create_row()
    row["underlying"] = " infy "

    result = parse_nse_option_row(row)

    assert result.underlying == " infy "