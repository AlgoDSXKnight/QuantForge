from datetime import date, datetime
from typing import Any, Mapping, Sequence

from app.pricing.historical_option_chain import (
    HistoricalOptionChainRow,
)


def _parse_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if not isinstance(value, str):
        raise ValueError(
            "Date value must be a string or date."
        )

    value = value.strip()

    formats = (
        "%d-%b-%Y %H:%M:%S",
        "%d-%b-%Y",
        "%d-%b-%y",
        "%Y-%m-%d",
        "%d/%m/%Y",
    )

    for date_format in formats:
        try:
            return datetime.strptime(
                value,
                date_format,
            ).date()
        except ValueError:
            continue

    raise ValueError(
        f"Unsupported date format: {value}"
    )


def _parse_float(
    value: Any,
    field_name: str,
) -> float:
    if value is None or value == "":
        raise ValueError(
            f"{field_name} cannot be empty."
        )

    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{field_name} must be numeric."
        ) from exc


def _normalize_option_type(value: str) -> str:
    option_type = value.strip().upper()

    mapping = {
        "CE": "CALL",
        "CALL": "CALL",
        "PE": "PUT",
        "PUT": "PUT",
    }

    if option_type not in mapping:
        raise ValueError(
            f"Unsupported NSE option type: {value}"
        )

    return mapping[option_type]


def parse_nse_option_row(
    row: Mapping[str, Any],
) -> HistoricalOptionChainRow:
    return HistoricalOptionChainRow(
        underlying=str(
            row["underlying"]
        ),
        timestamp=_parse_date(
            row["timestamp"]
        ),
        underlying_price=_parse_float(
            row["underlying_price"],
            "underlying_price",
        ),
        option_type=_normalize_option_type(
            str(row["option_type"])
        ),
        strike=_parse_float(
            row["strike"],
            "strike",
        ),
        expiration=_parse_date(
            row["expiration"]
        ),
        bid=_parse_float(
            row["bid"],
            "bid",
        ),
        ask=_parse_float(
            row["ask"],
            "ask",
        ),
        last_price=_parse_float(
            row["last_price"],
            "last_price",
        ),
    )


def parse_nse_option_rows(
    rows: Sequence[Mapping[str, Any]],
) -> list[HistoricalOptionChainRow]:
    if not rows:
        raise ValueError(
            "At least one NSE option row is required."
        )

    return [
        parse_nse_option_row(row)
        for row in rows
    ]