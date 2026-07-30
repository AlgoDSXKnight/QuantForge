from pydantic import BaseModel


class HoldingSummary(BaseModel):
    asset_name: str
    quantity: float


class PortfolioSummaryResponse(BaseModel):
    total_assets: int
    holdings: list[HoldingSummary]