from datetime import date

import yfinance as yf
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.historical_price import HistoricalPrice
from app.models.instrument import Instrument


def get_or_create_instrument(
    db: Session,
    symbol: str,
    name: str,
    exchange: str,
    asset_type: str,
) -> Instrument:
    symbol = symbol.strip().upper()

    instrument = db.scalar(
        select(Instrument).where(
            Instrument.symbol == symbol
        )
    )

    if instrument is not None:
        return instrument

    instrument = Instrument(
        symbol=symbol,
        name=name,
        exchange=exchange,
        asset_type=asset_type,
    )

    db.add(instrument)
    db.flush()

    return instrument


def ingest_historical_data(
    db: Session,
    symbol: str,
    start_date: date,
    end_date: date,
    name: str,
    exchange: str = "NSE",
    asset_type: str = "EQUITY",
) -> int:
    """
    Download daily historical OHLCV data and store it
    in the QuantForge database.

    Returns the number of newly inserted rows.
    """

    ticker = yf.Ticker(symbol)

    data = ticker.history(
        start=start_date,
        end=end_date,
        auto_adjust=False,
    )

    if data.empty:
        raise ValueError(
            f"No historical data found for {symbol}."
        )

    instrument = get_or_create_instrument(
        db=db,
        symbol=symbol,
        name=name,
        exchange=exchange,
        asset_type=asset_type,
    )

    existing_dates = set(
        db.scalars(
            select(HistoricalPrice.date).where(
                HistoricalPrice.instrument_id
                == instrument.id,
                HistoricalPrice.date >= start_date,
                HistoricalPrice.date < end_date,
            )
        ).all()
    )

    inserted_count = 0

    for timestamp, row in data.iterrows():
        price_date = timestamp.date()

        if price_date in existing_dates:
            continue

        historical_price = HistoricalPrice(
            instrument_id=instrument.id,
            date=price_date,
            open=float(row["Open"]),
            high=float(row["High"]),
            low=float(row["Low"]),
            close=float(row["Close"]),
            volume=float(row["Volume"]),
            adjusted_close=float(row["Adj Close"]),
        )

        db.add(historical_price)
        inserted_count += 1

    db.commit()

    return inserted_count
    