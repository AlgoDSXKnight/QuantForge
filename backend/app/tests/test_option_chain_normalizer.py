#@'
from datetime import date

import pytest

from app.pricing.option_chain_normalizer import (
    build_normalized_option_chain,
    normalize_option_chain_rows,
)


BASE_ROWS = [
    {
        "underlying": " infy ",
        "timestamp": "2026-09-01",
        "option_type": "ce",
        "strike": "1900",
        "expiration": "25-Sep-2026",
        "bid": "85.50",
        "ask": "90.50",
        "last_price": "88.00",
        "underlying_price": "1985",
    },
    {
        "underlying": "INFY",
        "timestamp": "2026-09-01",
        "option_type": "PE",
        "strike": "1900",
        "expiration": "25-Sep-2026",
        "bid": "12.00",
        "ask": "15.00",
        "last_price": "13.50",
        "underlying_price": "1985",
    },
]


def test_normalizes_underlying_and_option_type():
    options = normalize_option_chain_rows(BASE_ROWS)

    assert options[0].underlying == "INFY"
    assert {option.option_type for option in options} == {"CALL", "PUT"}


def test_normalizes_numeric_values():
    options = normalize_option_chain_rows(BASE_ROWS)

    assert options[0].strike == 1900.0
    assert options[0].bid == 85.5
    assert options[0].ask == 90.5
    assert options[0].last_price == 88.0
    assert options[0].underlying_price == 1985.0


def test_normalizes_supported_date_formats():
    rows = [dict(BASE_ROWS[0])]
    rows[0]["timestamp"] = "01/09/2026"
    rows[0]["expiration"] = date(2026, 9, 25)

    options = normalize_option_chain_rows(rows)

    assert options[0].timestamp == date(2026, 9, 1)
    assert options[0].expiration == date(2026, 9, 25)


def test_sorts_by_expiration_strike_and_option_type():
    rows = [
        dict(BASE_ROWS[0]),
        dict(BASE_ROWS[1]),
    ]

    rows[0]["strike"] = 2000
    rows[1]["strike"] = 1900

    options = normalize_option_chain_rows(rows)

    assert options[0].strike == 1900.0
    assert options[1].strike == 2000.0


def test_rejects_empty_rows():
    with pytest.raises(ValueError, match="At least one"):
        normalize_option_chain_rows([])


def test_rejects_invalid_option_type():
    rows = [dict(BASE_ROWS[0])]
    rows[0]["option_type"] = "XYZ"

    with pytest.raises(ValueError, match="Option type"):
        normalize_option_chain_rows(rows)


def test_rejects_non_finite_numeric_values():
    rows = [dict(BASE_ROWS[0])]
    rows[0]["bid"] = "nan"

    with pytest.raises(ValueError, match="finite"):
        normalize_option_chain_rows(rows)


def test_rejects_duplicate_contracts():
    rows = [
        dict(BASE_ROWS[0]),
        dict(BASE_ROWS[0]),
    ]

    with pytest.raises(ValueError, match="Duplicate option contract"):
        normalize_option_chain_rows(rows)


def test_rejects_mixed_underlyings():
    rows = [
        dict(BASE_ROWS[0]),
        dict(BASE_ROWS[1]),
    ]
    rows[1]["underlying"] = "TCS"

    with pytest.raises(ValueError, match="same underlying"):
        build_normalized_option_chain(rows)


def test_rejects_mixed_timestamps():
    rows = [
        dict(BASE_ROWS[0]),
        dict(BASE_ROWS[1]),
    ]
    rows[1]["timestamp"] = "2026-09-02"

    with pytest.raises(ValueError, match="same timestamp"):
        build_normalized_option_chain(rows)


def test_rejects_mixed_underlying_prices():
    rows = [
        dict(BASE_ROWS[0]),
        dict(BASE_ROWS[1]),
    ]
    rows[1]["underlying_price"] = 1990

    with pytest.raises(ValueError, match="same underlying price"):
        build_normalized_option_chain(rows)


def test_builds_normalized_option_chain():
    chain = build_normalized_option_chain(BASE_ROWS)

    assert chain.underlying == "INFY"
    assert chain.timestamp == date(2026, 9, 1)
    assert chain.underlying_price == 1985.0
    assert len(chain.options) == 2


def test_normalized_chain_contains_canonical_option_types():
    chain = build_normalized_option_chain(BASE_ROWS)

    assert len(chain.calls()) == 1
    assert len(chain.puts()) == 1
#'@ | Set-Content app\tests\test_option_chain_normalizer.py