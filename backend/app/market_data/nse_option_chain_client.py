from typing import Any

import requests

from app.core.market_data_exceptions import (
    NSEAccessError,
    NSEConnectionError,
    NSEMarketDataError,
    NSERateLimitError,
    NSEServerError,
)
from app.market_data.nse_option_chain import parse_nse_option_rows
from app.pricing.historical_option_chain import HistoricalOptionChainRow


NSE_BASE_URL = "https://www.nseindia.com"
NSE_OPTION_CHAIN_PAGE_URL = f"{NSE_BASE_URL}/option-chain"
NSE_OPTION_CHAIN_URL = (
    f"{NSE_BASE_URL}/api/option-chain-equities"
)


class NSEOptionChainClient:
    def __init__(self, timeout: float = 10.0) -> None:
        if timeout <= 0:
            raise ValueError("Timeout must be greater than zero.")

        self.timeout = timeout

    def _create_session(self) -> requests.Session:
        session = requests.Session()

        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/142.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,image/avif,image/webp,"
                    "image/apng,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache",
            }
        )

        return session

    def _get(
        self,
        session: requests.Session,
        url: str,
        **kwargs: Any,
    ) -> requests.Response:
        try:
            response = session.get(
                url,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise NSEConnectionError(
                f"Unable to connect to NSE: {exc}"
            ) from exc

        status_code = response.status_code

        if status_code in {401, 403}:
            raise NSEAccessError(
                f"NSE rejected access with HTTP {status_code}."
            )

        if status_code == 429:
            raise NSERateLimitError(
                "NSE rate limit exceeded (HTTP 429)."
            )

        if 500 <= status_code <= 599:
            raise NSEServerError(
                f"NSE returned server error HTTP {status_code}."
            )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise NSEMarketDataError(
                f"NSE request failed with HTTP {status_code}."
            ) from exc

        return response

    def _initialize_session(
        self,
        session: requests.Session,
    ) -> None:
        homepage_response = self._get(
            session,
            NSE_BASE_URL,
        )

        option_chain_response = self._get(
            session,
            NSE_OPTION_CHAIN_PAGE_URL,
            headers={
                "Referer": NSE_BASE_URL,
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,image/avif,image/webp,"
                    "image/apng,*/*;q=0.8"
                ),
            },
        )

        # Keep references alive until initialization completes.
        _ = homepage_response
        _ = option_chain_response

    def fetch_raw(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError("Symbol cannot be empty.")

        session = self._create_session()

        self._initialize_session(session)

        response = self._get(
            session,
            NSE_OPTION_CHAIN_URL,
            params={"symbol": symbol},
            headers={
                "Referer": NSE_OPTION_CHAIN_PAGE_URL,
                "Accept": "application/json,text/plain,*/*",
                "X-Requested-With": "XMLHttpRequest",
            },
        )

        try:
            data = response.json()
        except ValueError as exc:
            raise NSEMarketDataError(
                "NSE response was not valid JSON."
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(
                "NSE response must be a JSON object."
            )

        return data

    def fetch_rows(
        self,
        symbol: str,
    ) -> list[HistoricalOptionChainRow]:
        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError("Symbol cannot be empty.")

        data = self.fetch_raw(symbol)

        records = data.get("records")

        if not isinstance(records, dict):
            raise ValueError(
                "NSE response does not contain records."
            )

        timestamp = records.get("timestamp")
        underlying_price = records.get("underlyingValue")
        rows = records.get("data")

        if not timestamp:
            raise ValueError(
                "NSE response does not contain timestamp."
            )

        if underlying_price is None:
            raise ValueError(
                "NSE response does not contain underlyingValue."
            )

        if not isinstance(rows, list):
            raise ValueError(
                "NSE response does not contain option-chain data."
            )

        normalized_rows: list[dict[str, Any]] = []

        for item in rows:
            if not isinstance(item, dict):
                continue

            strike = item.get("strikePrice")
            expiration = item.get("expiryDate")

            if strike is None or expiration is None:
                continue

            for option_key in ("CE", "PE"):
                option_data = item.get(option_key)

                if not isinstance(option_data, dict):
                    continue

                normalized_rows.append(
                    {
                        "underlying": symbol,
                        "timestamp": timestamp,
                        "underlying_price": underlying_price,
                        "option_type": option_key,
                        "strike": strike,
                        "expiration": expiration,
                        "bid": option_data.get("bidprice", 0.0),
                        "ask": option_data.get("askPrice", 0.0),
                        "last_price": option_data.get("lastPrice", 0.0),
                    }
                )

        if not normalized_rows:
            raise ValueError(
                "NSE response contained no option contracts."
            )

        return parse_nse_option_rows(normalized_rows)