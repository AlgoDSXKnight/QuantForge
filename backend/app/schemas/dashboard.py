from datetime import datetime

from pydantic import BaseModel

from app.schemas.holding import HoldingResponse


class RecentTransaction(BaseModel):
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


class DashboardSummary(BaseModel):
    total_portfolios: int
    total_transactions: int
    total_assets: int

    total_invested: float
    current_value: float
    profit_loss: float
    profit_loss_percent: float

    holdings: list[HoldingResponse]
    recent_transactions: list[RecentTransaction]


class PortfolioPerformanceSummary(BaseModel):
    portfolio_id: int
    portfolio_name: str

    invested: float
    current_value: float
    profit_loss: float
    profit_loss_percent: float

