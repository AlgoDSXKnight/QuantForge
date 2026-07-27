from datetime import datetime

from pydantic import BaseModel


class TransactionCreate(BaseModel):
    asset_name: str
    transaction_type: str
    quantity: float
    price: float
    portfolio_id: int


class TransactionUpdate(BaseModel):
    asset_name: str
    transaction_type: str
    quantity: float
    price: float


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