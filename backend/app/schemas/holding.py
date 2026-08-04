from pydantic import BaseModel


class HoldingResponse(BaseModel):
    asset_name: str
    quantity: float
    average_buy_price: float
    invested_amount: float