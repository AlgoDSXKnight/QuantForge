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

class PortfolioPerformance(BaseModel):
    portfolio_name: str

    invested: float
    current_value: float

    profit_loss: float
    profit_loss_percent: float

class AssetAllocation(BaseModel):
    asset_name: str
    current_value: float
    allocation_percent: float