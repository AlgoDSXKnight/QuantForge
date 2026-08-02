from pydantic import BaseModel


class PortfolioCreate(BaseModel):
    name: str


class PortfolioUpdate(BaseModel):
    name: str


class PortfolioResponse(BaseModel):
    id: int
    name: str
    user_id: int

    model_config = {
        "from_attributes": True,
    }

class PortfolioSummary(BaseModel):
    portfolio_name: str
    total_transactions: int
    total_holdings: int
    total_quantity: float
    total_invested: float