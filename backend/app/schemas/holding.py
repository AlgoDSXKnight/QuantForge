from pydantic import BaseModel


class HoldingResponse(BaseModel):
    asset_name: str
    quantity: float