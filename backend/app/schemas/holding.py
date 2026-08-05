from pydantic import BaseModel


class HoldingResponse(BaseModel):
    asset_name: str
    quantity: float

    average_buy_price: float
    invested_amount: float

    current_price: float
    current_value: float

    profit_loss: float
    profit_loss_percent: float