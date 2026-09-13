from datetime import date

# pyrefly: ignore [missing-import]
from sqlalchemy import (
    Date,
    Float,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class HistoricalPrice(Base):
    __tablename__ = "historical_prices"

    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "date",
            name="uq_historical_price_instrument_date",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id"),
        nullable=False,
        index=True,
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    open: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    high: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    low: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    close: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    volume: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    adjusted_close: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    instrument: Mapped["Instrument"] = relationship(
        back_populates="historical_prices",
    )