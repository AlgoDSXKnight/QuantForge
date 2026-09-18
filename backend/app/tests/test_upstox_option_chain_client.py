from datetime import date
from unittest.mock import Mock, patch

import pytest
import requests

from app.market_data.upstox_option_chain_client import (
    UpstoxAccessError,
    UpstoxConnectionError,
    UpstoxOptionChainClient,
    UpstoxRateLimitError,
    UpstoxServerError,
    parse_upstox_option_chain,
)


PAYLOAD = {
    "status": "success",
    "data": [
        {
            "expiry": "2026-09-24",
            "strike_price": 1950,
            "underlying_key": "NSE_INDEX|NIFTY 50",
            "underlying_spot_price": 1985.0,
            "call_options": {
                "market_data": {
                    "ltp": 82.5,
                    "bid_price": 81.0,
                    "ask_price": 84.0,
                }
            },
            "put_options": {
                "market_data": {
                    "ltp": 31.5,
                    "bid_price": 30.0,
                    "ask_price": 33.0,
                }
            },
        },
    ],
}


def test_parse_upstox_option_chain():
    chain = parse_upstox_option_chain(
        PAYLOAD,
        timestamp=date(2026, 9, 18),
    )

    assert chain.underlying == "NIFTY 50"
    assert chain.timestamp == date(2026, 9, 18)
    assert chain.underlying_price == 1985.0
    assert len(chain.options) == 2


def test_parse_upstox_call():
    chain = parse_upstox_option_chain(
        PAYLOAD,
        timestamp=date(2026, 9, 18),
    )

    call = chain.calls()[0]

    assert call.option_type == "CALL"
    assert call.strike == 1950.0
    assert call.bid == 81.0
    assert call.ask == 84.0
    assert call.last_price == 82.5


def test_parse_upstox_put():
    chain = parse_upstox_option_chain(
        PAYLOAD,
        timestamp=date(2026, 9, 18),
    )

    put = chain.puts()[0]

    assert put.option_type == "PUT"
    assert put.strike == 1950.0
    assert put.bid == 30.0
    assert put.ask == 33.0
    assert put.last_price == 31.5


def test_rejects_empty_response():
    with pytest.raises(ValueError, match="no data"):
        parse_upstox_option_chain(
            {"status": "success", "data": []},
            timestamp=date(2026, 9, 18),
        )


def test_rejects_response_without_contracts():
    payload = {
        "status": "success",
        "data": [
            {
                "expiry": "2026-09-24",
                "strike_price": 1950,
                "underlying_key": "NSE_INDEX|NIFTY 50",
                "underlying_spot_price": 1985.0,
            }
        ],
    }

    with pytest.raises(ValueError, match="no option contracts"):
        parse_upstox_option_chain(
            payload,
            timestamp=date(2026, 9, 18),
        )


def test_client_requires_token():
    with pytest.raises(ValueError, match="access token"):
        UpstoxOptionChainClient("")


def test_client_rejects_empty_instrument_key():
    client = UpstoxOptionChainClient("test-token")

    with pytest.raises(ValueError, match="Instrument key"):
        client.fetch_raw("", "2026-09-24")


def test_client_rejects_empty_expiry():
    client = UpstoxOptionChainClient("test-token")

    with pytest.raises(ValueError, match="Expiry"):
        client.fetch_raw("NSE_INDEX|NIFTY 50", "")


@patch("app.market_data.upstox_option_chain_client.requests.get")
def test_client_fetch_raw_success(mock_get):
    response = Mock()
    response.status_code = 200
    response.json.return_value = PAYLOAD
    mock_get.return_value = response

    client = UpstoxOptionChainClient("test-token")

    result = client.fetch_raw(
        "NSE_INDEX|NIFTY 50",
        "2026-09-24",
    )

    assert result == PAYLOAD
    mock_get.assert_called_once()


@patch("app.market_data.upstox_option_chain_client.requests.get")
def test_client_maps_auth_error(mock_get):
    response = Mock()
    response.status_code = 401
    mock_get.return_value = response

    client = UpstoxOptionChainClient("test-token")

    with pytest.raises(UpstoxAccessError):
        client.fetch_raw(
            "NSE_INDEX|NIFTY 50",
            "2026-09-24",
        )


@patch("app.market_data.upstox_option_chain_client.requests.get")
def test_client_maps_rate_limit(mock_get):
    response = Mock()
    response.status_code = 429
    mock_get.return_value = response

    client = UpstoxOptionChainClient("test-token")

    with pytest.raises(UpstoxRateLimitError):
        client.fetch_raw(
            "NSE_INDEX|NIFTY 50",
            "2026-09-24",
        )


@patch("app.market_data.upstox_option_chain_client.requests.get")
def test_client_maps_server_error(mock_get):
    response = Mock()
    response.status_code = 500
    mock_get.return_value = response

    client = UpstoxOptionChainClient("test-token")

    with pytest.raises(UpstoxServerError):
        client.fetch_raw(
            "NSE_INDEX|NIFTY 50",
            "2026-09-24",
        )


@patch("app.market_data.upstox_option_chain_client.requests.get")
def test_client_maps_connection_error(mock_get):
    mock_get.side_effect = requests.RequestException()

    client = UpstoxOptionChainClient("test-token")

    with pytest.raises(UpstoxConnectionError):
        client.fetch_raw(
            "NSE_INDEX|NIFTY 50",
            "2026-09-24",
        )


@patch("app.market_data.upstox_option_chain_client.requests.get")
def test_client_fetch_chain(mock_get):
    response = Mock()
    response.status_code = 200
    response.json.return_value = PAYLOAD
    mock_get.return_value = response

    client = UpstoxOptionChainClient("test-token")

    chain = client.fetch_chain(
        "NSE_INDEX|NIFTY 50",
        "2026-09-24",
        timestamp=date(2026, 9, 18),
    )

    assert chain.underlying == "NIFTY 50"
    assert len(chain.options) == 2
