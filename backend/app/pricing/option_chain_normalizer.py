#'@ 
from datetime import date, datetime
from math import isfinite
from typing import Any

from app.pricing.option_chain import OptionChain
from app.pricing.option_market_data import OptionMarketData


def _normalize_text(value: Any, field_name: str) -> str:
    if value is None:
        raise ValueError(f"{field_name} is required.")
    result = str(value).strip().upper()
    if not result:
        raise ValueError(f"{field_name} cannot be empty.")
    return result


def _normalize_option_type(value: Any) -> str:
    option_type = _normalize_text(value, "Option type")
    aliases = {
        "CE": "CALL",
        "CALL": "CALL",
        "PE": "PUT",
        "PUT": "PUT",
    }
    if option_type not in aliases:
        raise ValueError("Option type must be CALL, PUT, CE, or PE.")
    return aliases[option_type]


def _normalize_date(value: Any, field_name: str) -> date:
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if value is None:
        raise ValueError(f"{field_name} is required.")

    text = str(value).strip()

    formats = (
        "%Y-%m-%d",
        "%d-%b-%Y",
        "%d-%b-%y",
        "%d/%m/%Y",
        "%d/%m/%y",
    )

    for date_format in formats:
        try:
            return datetime.strptime(text, date_format).date()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(text).date()
    except ValueError as exc:
        raise ValueError(
            f"Invalid {field_name}: {value}"
        ) from exc


def _normalize_float(value: Any, field_name: str) -> float:
    if value is None:
        raise ValueError(f"{field_name} is required.")

    if isinstance(value, str):
        value = value.strip().replace(",", "")

    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{field_name} must be numeric."
        ) from exc

    if not isfinite(result):
        raise ValueError(f"{field_name} must be finite.")

    return result


def _normalize_row(row: dict[str, Any]) -> OptionMarketData:
    if not isinstance(row, dict):
        raise ValueError("Each option-chain row must be a dictionary.")

    underlying = _normalize_text(
        row.get("underlying"),
        "Underlying",
    )

    timestamp = _normalize_date(
        row.get("timestamp"),
        "Timestamp",
    )

    option_type = _normalize_option_type(
        row.get("option_type")
    )

    strike = _normalize_float(
        row.get("strike"),
        "Strike",
    )

    expiration = _normalize_date(
        row.get("expiration"),
        "Expiration",
    )

    bid = _normalize_float(
        row.get("bid"),
        "Bid",
    )

    ask = _normalize_float(
        row.get("ask"),
        "Ask",
    )

    last_price = _normalize_float(
        row.get("last_price"),
        "Last price",
    )

    underlying_price = _normalize_float(
        row.get("underlying_price"),
        "Underlying price",
    )

    return OptionMarketData(
        underlying=underlying,
        timestamp=timestamp,
        option_type=option_type,
        strike=strike,
        expiration=expiration,
        bid=bid,
        ask=ask,
        last_price=last_price,
        underlying_price=underlying_price,
    )


def normalize_option_chain_rows(
    rows: list[dict[str, Any]],
) -> list[OptionMarketData]:
    if not rows:
        raise ValueError("At least one option-chain row is required.")

    normalized: list[OptionMarketData] = []
    seen: set[tuple[str, date, str, float, date]] = set()

    for row in rows:
        option = _normalize_row(row)

        key = (
            option.underlying,
            option.timestamp,
            option.option_type,
            option.strike,
            option.expiration,
        )

        if key in seen:
            raise ValueError(
                "Duplicate option contract detected: "
                f"{option.underlying} "
                f"{option.expiration} "
                f"{option.option_type} "
                f"{option.strike}"
            )

        seen.add(key)
        normalized.append(option)

    normalized.sort(
        key=lambda option: (
            option.expiration,
            option.strike,
            option.option_type,
        )
    )

    return normalized


def build_normalized_option_chain(
    rows: list[dict[str, Any]],
) -> OptionChain:
    options = normalize_option_chain_rows(rows)

    underlying = options[0].underlying
    timestamp = options[0].timestamp
    underlying_price = options[0].underlying_price

    for option in options:
        if option.underlying != underlying:
            raise ValueError(
                "All option-chain rows must have the same underlying."
            )

        if option.timestamp != timestamp:
            raise ValueError(
                "All option-chain rows must have the same timestamp."
            )

        if option.underlying_price != underlying_price:
            raise ValueError(
                "All option-chain rows must have the same underlying price."
            )

    return OptionChain(
        underlying=underlying,
        timestamp=timestamp,
        underlying_price=underlying_price,
        options=options,
    )
#'@ | Set-Content app\pricing\option_chain_normalizer.py