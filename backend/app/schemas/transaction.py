from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TransactionCreate(BaseModel):
    asset_name: str = Field(min_length=1, max_length=100)
    transaction_type: Literal["BUY", "SELL"]
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)
    portfolio_id: int = Field(gt=0)

    @field_validator("asset_name")
    @classmethod
    def normalize_asset_name(cls, value: str) -> str:
        return value.strip().upper()


class TransactionUpdate(BaseModel):
    asset_name: str = Field(min_length=1, max_length=100)
    transaction_type: Literal["BUY", "SELL"]
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)

    @field_validator("asset_name")
    @classmethod
    def normalize_asset_name(cls, value: str) -> str:
        return value.strip().upper()


class TransactionResponse(BaseModel):
    id: int
    asset_name: str
    transaction_type: str
    quantity: float
    price: float
    transaction_date: datetime
    portfolio_id: int

    model_config = {
        "from_attributes": True,
    }
