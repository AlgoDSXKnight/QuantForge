from types import SimpleNamespace

import pytest

from app.services.portfolio_calculation_service import (
    calculate_holdings,
    calculate_portfolio_totals,
)


def transaction(
    asset_name: str,
    transaction_type: str,
    quantity: float,
    price: float,
):
    return SimpleNamespace(
        id=None,
        asset_name=asset_name,
        transaction_type=transaction_type,
        quantity=quantity,
        price=price,
    )


def test_buy_transaction():
    transactions = [
        transaction(
            "INFY",
            "BUY",
            10,
            1900,
        ),
    ]

    result = calculate_holdings(transactions)

    assert result == {
        "INFY": {
            "quantity": 10.0,
            "invested": 19000.0,
        },
    }


def test_multiple_buys():
    transactions = [
        transaction(
            "INFY",
            "BUY",
            10,
            1900,
        ),
        transaction(
            "INFY",
            "BUY",
            5,
            2000,
        ),
    ]

    result = calculate_holdings(transactions)

    assert result == {
        "INFY": {
            "quantity": 15.0,
            "invested": 29000.0,
        },
    }


def test_sell_uses_average_cost_basis():
    transactions = [
        transaction(
            "INFY",
            "BUY",
            10,
            1900,
        ),
        transaction(
            "INFY",
            "BUY",
            10,
            1900,
        ),
        transaction(
            "INFY",
            "BUY",
            5,
            1900,
        ),
        transaction(
            "INFY",
            "SELL",
            5,
            2000,
        ),
    ]

    result = calculate_holdings(transactions)

    assert result == {
        "INFY": {
            "quantity": 20.0,
            "invested": 38000.0,
        },
    }


def test_sell_more_than_holdings_fails():
    transactions = [
        transaction(
            "INFY",
            "BUY",
            5,
            1900,
        ),
        transaction(
            "INFY",
            "SELL",
            10,
            2000,
        ),
    ]

    with pytest.raises(ValueError):
        calculate_holdings(transactions)


def test_multiple_assets():
    transactions = [
        transaction(
            "INFY",
            "BUY",
            20,
            1900,
        ),
        transaction(
            "TCS",
            "BUY",
            10,
            4100,
        ),
    ]

    result = calculate_holdings(transactions)

    assert result == {
        "INFY": {
            "quantity": 20.0,
            "invested": 38000.0,
        },
        "TCS": {
            "quantity": 10.0,
            "invested": 41000.0,
        },
    }


def test_completely_sold_position_is_removed():
    transactions = [
        transaction(
            "INFY",
            "BUY",
            10,
            1900,
        ),
        transaction(
            "INFY",
            "SELL",
            10,
            2000,
        ),
    ]

    result = calculate_holdings(transactions)

    assert result == {}


def test_transaction_type_is_normalized():
    transactions = [
        transaction(
            " infy ",
            " buy ",
            10,
            1900,
        ),
    ]

    result = calculate_holdings(transactions)

    assert result == {
        "INFY": {
            "quantity": 10.0,
            "invested": 19000.0,
        },
    }


def test_unsupported_transaction_type_fails():
    transactions = [
        transaction(
            "INFY",
            "TRANSFER",
            10,
            1900,
        ),
    ]

    with pytest.raises(ValueError):
        calculate_holdings(transactions)


def test_portfolio_totals():
    holdings = {
        "INFY": {
            "quantity": 20.0,
            "invested": 38000.0,
        },
        "TCS": {
            "quantity": 10.0,
            "invested": 41000.0,
        },
    }

    result = calculate_portfolio_totals(holdings)

    assert result == {
        "total_quantity": 30.0,
        "total_invested": 79000.0,
    }