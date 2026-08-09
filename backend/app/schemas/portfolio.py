from pydantic import BaseModel, Field, field_validator


class PortfolioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return value.strip()


class PortfolioUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return value.strip()


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


class PortfolioHistory(BaseModel):
    date: str
    invested: float
    current_value: float
