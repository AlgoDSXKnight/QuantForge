from datetime import date
from typing import Any

import requests

from app.pricing.option_chain_normalizer import build_normalized_option_chain
from app.pricing.option_chain import OptionChain


UPSTOX_OPTION_CHAIN_URL = "https://api.upstox.com/v2/option/chain"


class UpstoxMarketDataError(Exception):
    """Base exception for Upstox market-data errors."""


class UpstoxAccessError(UpstoxMarketDataError):
    """Raised when Upstox rejects authentication or authorization."""


class UpstoxRateLimitError(UpstoxMarketDataError):
    """Raised when Upstox rate-limits the request."""


class UpstoxServerError(UpstoxMarketDataError):
    """Raised when Upstox returns a server-side error."""


class UpstoxConnectionError(UpstoxMarketDataError):
    """Raised when Upstox cannot be reached."""


class UpstoxOptionChainClient:
    def __init__(
        self,
        access_token: str,
        timeout: float = 10.0,
    ) -> None:
        token = access_token.strip()

        if not token:
            raise ValueError("Upstox access token cannot be empty.")

        if timeout <= 0:
            raise ValueError("Timeout must be greater than zero.")

        self.access_token = token
        self.timeout = timeout

    def fetch_raw(
        self,
        instrument_key: str,
        expiry_date: str,
    ) -> dict[str, Any]:
        instrument_key = instrument_key.strip()
        expiry_date = expiry_date.strip()

        if not instrument_key:
            raise ValueError("Instrument key cannot be empty.")

        if not expiry_date:
            raise ValueError("Expiry date cannot be empty.")

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        params = {
            "instrument_key": instrument_key,
            "expiry_date": expiry_date,
        }

        try:
            response = requests.get(
                UPSTOX_OPTION_CHAIN_URL,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise UpstoxConnectionError(
                "Unable to connect to Upstox."
            ) from exc

        if response.status_code in {401, 403}:
            raise UpstoxAccessError(
                "Upstox rejected the request."
            )

        if response.status_code == 429:
            raise UpstoxRateLimitError(
                "Upstox rate limit exceeded."
            )

        if response.status_code >= 500:
            raise UpstoxServerError(
                f"Upstox server error: {response.status_code}."
            )

        if response.status_code >= 400:
            raise UpstoxMarketDataError(
                f"Upstox request failed: {response.status_code}."
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise UpstoxMarketDataError(
                "Upstox returned invalid JSON."
            ) from exc

        if payload.get("status") != "success":
            raise UpstoxMarketDataError(
                "Upstox returned an unsuccessful response."
            )

        return payload

    def fetch_chain(
        self,
        instrument_key: str,
        expiry_date: str,
        timestamp: date | None = None,
    ) -> OptionChain:
        payload = self.fetch_raw(
            instrument_key=instrument_key,
            expiry_date=expiry_date,
        )

        return parse_upstox_option_chain(
            payload,
            timestamp=timestamp or date.today(),
        )


def _parse_option_row(
    row: dict[str, Any],
    option_type: str,
    timestamp: date,
) -> dict[str, Any] | None:
    option_data = row.get(
        "call_options" if option_type == "CALL" else "put_options"
    )

    if not option_data:
        return None

    market_data = option_data.get("market_data", {})

    return {
        "underlying": row["underlying_key"].split("|")[-1],
        "timestamp": timestamp,
        "option_type": option_type,
        "strike": row["strike_price"],
        "expiration": row["expiry"],
        "bid": market_data.get("bid_price", 0.0),
        "ask": market_data.get("ask_price", 0.0),
        "last_price": market_data.get("ltp", 0.0),
        "underlying_price": row["underlying_spot_price"],
    }


def parse_upstox_option_chain(
    payload: dict[str, Any],
    timestamp: date,
) -> OptionChain:
    data = payload.get("data")

    if not isinstance(data, list) or not data:
        raise ValueError("Upstox option-chain response contains no data.")

    rows: list[dict[str, Any]] = []

    for item in data:
        if not isinstance(item, dict):
            continue

        for option_type in ("CALL", "PUT"):
            row = _parse_option_row(
                item,
                option_type,
                timestamp,
            )

            if row is not None:
                rows.append(row)

    if not rows:
        raise ValueError(
            "Upstox option-chain response contains no option contracts."
        )

    return build_normalized_option_chain(rows)