from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.portfolio import Portfolio
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.summary import (
    HoldingSummary,
    PortfolioSummaryResponse,
)

router = APIRouter(
    prefix="/portfolio-summary",
    tags=["Portfolio Summary"],
)

@router.get(
    "/",
    response_model=PortfolioSummaryResponse,
)
def get_portfolio_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = (
        db.query(Transaction)
        .join(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .all()
    )

    holdings = {}

    for transaction in transactions:

        asset = transaction.asset_name

        if asset not in holdings:
            holdings[asset] = 0

        if transaction.transaction_type == "BUY":
            holdings[asset] += transaction.quantity
        else:
            holdings[asset] -= transaction.quantity

    holdings_response = [
        HoldingSummary(
            asset_name=asset,
            quantity=quantity,
        )
        for asset, quantity in holdings.items()
        if quantity > 0
    ]

    return PortfolioSummaryResponse(
        total_assets=len(holdings_response),
        holdings=holdings_response,
    )