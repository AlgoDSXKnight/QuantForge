from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_portfolios: int
    total_transactions: int
    total_assets: int
    total_invested: float