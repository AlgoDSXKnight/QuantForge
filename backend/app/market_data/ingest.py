import argparse
from datetime import date

from app.database.session import SessionLocal
from app.services.market_data_service import ingest_historical_data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest historical market data into QuantForge."
    )

    parser.add_argument(
        "symbol",
        help="Yahoo Finance symbol, e.g. INFY.NS",
    )

    parser.add_argument(
        "start_date",
        help="Start date in YYYY-MM-DD format",
    )

    parser.add_argument(
        "end_date",
        help="End date in YYYY-MM-DD format",
    )

    parser.add_argument(
        "--name",
        required=True,
        help="Instrument name, e.g. Infosys",
    )

    args = parser.parse_args()

    start_date = date.fromisoformat(args.start_date)
    end_date = date.fromisoformat(args.end_date)

    if start_date >= end_date:
        raise ValueError(
            "Start date must be before end date."
        )

    db = SessionLocal()

    try:
        inserted_count = ingest_historical_data(
            db=db,
            symbol=args.symbol,
            start_date=start_date,
            end_date=end_date,
            name=args.name,
        )

        print(
            f"Successfully ingested {inserted_count} "
            f"new rows for {args.symbol.upper()}."
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()