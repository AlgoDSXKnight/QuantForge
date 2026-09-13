from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Instrument(Base):
    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    symbol: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    exchange: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    asset_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    historical_prices: Mapped[list["HistoricalPrice"]] = (
        relationship(
            back_populates="instrument",
            cascade="all, delete-orphan",
        )
    )