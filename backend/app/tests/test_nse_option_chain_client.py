from unittest.mock import Mock, patch

import pytest

from app.core.market_data_exceptions import (
    NSEAccessError,
    NSEConnectionError,
    NSEMarketDataError,
    NSERateLimitError,
    NSEServerError,
)
from app.market_data.nse_option_chain_client import NSEOptionChainClient


def create_response() -> dict:
    return {
        "records": {
            "timestamp": "01-Jun-2026 15:30:00",
            "underlyingValue": 1900.0,
            "data": [
                {
                    "strikePrice": 1900.0,
                    "expiryDate": "25-Jun-2026",
                    "CE": {
                        "bidprice": 20.0,
                        "askPrice": 21.0,
                        "lastPrice": 20.5,
                    },
                    "PE": {
                        "bidprice": 19.0,
                        "askPrice": 20.0,
                        "lastPrice": 19.5,
                    },
                },
                {
                    "strikePrice": 2000.0,
                    "expiryDate": "25-Jun-2026",
                    "CE": {
                        "bidprice": 5.0,
                        "askPrice": 6.0,
                        "lastPrice": 5.5,
                    },
                    "PE": {
                        "bidprice": 100.0,
                        "askPrice": 101.0,
                        "lastPrice": 100.5,
                    },
                },
            ],
        }
    }


def create_mock_response(
    payload: dict | None = None,
    status_code: int = 200,
) -> Mock:
    response = Mock()
    response.status_code = status_code
    response.json.return_value = (
        payload if payload is not None else create_response()
    )
    response.raise_for_status.return_value = None
    return response


def test_fetch_raw() -> None:
    client = NSEOptionChainClient()

    homepage_response = create_mock_response()
    option_chain_page_response = create_mock_response()
    api_response = create_mock_response()

    with patch(
        "app.market_data.nse_option_chain_client.requests.Session"
    ) as session_class:
        session = session_class.return_value

        session.get.side_effect = [
            homepage_response,
            option_chain_page_response,
            api_response,
        ]

        result = client.fetch_raw(" infy ")

    assert result == create_response()
    assert session.get.call_count == 3

    assert session.get.call_args_list[0].args == (
        "https://www.nseindia.com",
    )

    assert session.get.call_args_list[1].args == (
        "https://www.nseindia.com/option-chain",
    )

    assert session.get.call_args_list[2].args == (
        "https://www.nseindia.com/api/option-chain-equities",
    )

    assert session.get.call_args_list[2].kwargs["params"] == {
        "symbol": "INFY"
    }


def test_fetch_rows() -> None:
    client = NSEOptionChainClient()

    api_response = create_mock_response()

    with patch(
        "app.market_data.nse_option_chain_client.requests.Session"
    ) as session_class:
        session = session_class.return_value

        session.get.side_effect = [
            create_mock_response(),
            create_mock_response(),
            api_response,
        ]

        rows = client.fetch_rows("INFY")

    assert len(rows) == 4

    assert rows[0].underlying == "INFY"
    assert rows[0].option_type == "CALL"
    assert rows[0].strike == 1900.0
    assert rows[0].bid == 20.0
    assert rows[0].ask == 21.0
    assert rows[0].last_price == 20.5

    assert rows[1].option_type == "PUT"
    assert rows[1].strike == 1900.0

    assert rows[2].option_type == "CALL"
    assert rows[2].strike == 2000.0

    assert rows[3].option_type == "PUT"
    assert rows[3].strike == 2000.0


def test_rejects_empty_symbol() -> None:
    client = NSEOptionChainClient()

    with pytest.raises(
        ValueError,
        match="Symbol cannot be empty",
    ):
        client.fetch_raw("   ")


def test_rejects_invalid_timeout() -> None:
    with pytest.raises(
        ValueError,
        match="Timeout must be greater than zero",
    ):
        NSEOptionChainClient(timeout=0)


def test_rejects_invalid_response_type() -> None:
    client = NSEOptionChainClient()

    response = create_mock_response()
    response.json.return_value = []

    with patch(
        "app.market_data.nse_option_chain_client.requests.Session"
    ) as session_class:
        session = session_class.return_value

        session.get.side_effect = [
            create_mock_response(),
            create_mock_response(),
            response,
        ]

        with pytest.raises(
            ValueError,
            match="NSE response must be a JSON object",
        ):
            client.fetch_raw("INFY")


def test_rejects_missing_timestamp() -> None:
    client = NSEOptionChainClient()

    payload = create_response()
    payload["records"].pop("timestamp")

    response = create_mock_response(payload)

    with patch(
        "app.market_data.nse_option_chain_client.requests.Session"
    ) as session_class:
        session = session_class.return_value

        session.get.side_effect = [
            create_mock_response(),
            create_mock_response(),
            response,
        ]

        with pytest.raises(
            ValueError,
            match="NSE response does not contain timestamp",
        ):
            client.fetch_rows("INFY")


def test_rejects_missing_underlying_value() -> None:
    client = NSEOptionChainClient()

    payload = create_response()
    payload["records"].pop("underlyingValue")

    response = create_mock_response(payload)

    with patch(
        "app.market_data.nse_option_chain_client.requests.Session"
    ) as session_class:
        session = session_class.return_value

        session.get.side_effect = [
            create_mock_response(),
            create_mock_response(),
            response,
        ]

        with pytest.raises(
            ValueError,
            match="NSE response does not contain underlyingValue",
        ):
            client.fetch_rows("INFY")


def test_rejects_missing_option_data() -> None:
    client = NSEOptionChainClient()

    payload = create_response()
    payload["records"]["data"] = []

    response = create_mock_response(payload)

    with patch(
        "app.market_data.nse_option_chain_client.requests.Session"
    ) as session_class:
        session = session_class.return_value

        session.get.side_effect = [
            create_mock_response(),
            create_mock_response(),
            response,
        ]

        with pytest.raises(
            ValueError,
            match="NSE response contained no option contracts",
        ):
            client.fetch_rows("INFY")


def test_http_access_error() -> None:
    client = NSEOptionChainClient()

    response = create_mock_response(status_code=403)

    with patch(
        "app.market_data.nse_option_chain_client.requests.Session"
    ) as session_class:
        session = session_class.return_value
        session.get.return_value = response

        with pytest.raises(
            NSEAccessError,
            match="NSE rejected access with HTTP 403",
        ):
            client.fetch_raw("INFY")


def test_http_rate_limit_error() -> None:
    client = NSEOptionChainClient()

    response = create_mock_response(status_code=429)

    with patch(
        "app.market_data.nse_option_chain_client.requests.Session"
    ) as session_class:
        session = session_class.return_value
        session.get.return_value = response

        with pytest.raises(
            NSERateLimitError,
            match="NSE rate limit exceeded",
        ):
            client.fetch_raw("INFY")


def test_http_server_error() -> None:
    client = NSEOptionChainClient()

    response = create_mock_response(status_code=500)

    with patch(
        "app.market_data.nse_option_chain_client.requests.Session"
    ) as session_class:
        session = session_class.return_value
        session.get.return_value = response

        with pytest.raises(
            NSEServerError,
            match="NSE returned server error HTTP 500",
        ):
            client.fetch_raw("INFY")


def test_http_other_error() -> None:
    client = NSEOptionChainClient()

    response = create_mock_response(status_code=400)

    with patch(
        "app.market_data.nse_option_chain_client.requests.Session"
    ) as session_class:
        session = session_class.return_value
        session.get.return_value = response

        response.raise_for_status.side_effect = __import__(
            "requests"
        ).HTTPError("400 Client Error")

        with pytest.raises(
            NSEMarketDataError,
            match="NSE request failed with HTTP 400",
        ):
            client.fetch_raw("INFY")


def test_connection_error() -> None:
    client = NSEOptionChainClient()

    with patch(
        "app.market_data.nse_option_chain_client.requests.Session"
    ) as session_class:
        session = session_class.return_value
        session.get.side_effect = (
            __import__("requests").RequestException("connection failed")
        )

        with pytest.raises(
            NSEConnectionError,
            match="Unable to connect to NSE",
        ):
            client.fetch_raw("INFY")


def test_invalid_json_response() -> None:
    client = NSEOptionChainClient()

    response = create_mock_response()

    response.json.side_effect = ValueError("invalid json")

    with patch(
        "app.market_data.nse_option_chain_client.requests.Session"
    ) as session_class:
        session = session_class.return_value

        session.get.side_effect = [
            create_mock_response(),
            create_mock_response(),
            response,
        ]

        with pytest.raises(
            NSEMarketDataError,
            match="NSE response was not valid JSON",
        ):
            client.fetch_raw("INFY")