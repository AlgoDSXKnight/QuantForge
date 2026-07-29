from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.transaction import Transaction
from app.models.portfolio import Portfolio
from app.models.user import User
from app.schemas.holding import HoldingResponse

router = APIRouter(
    prefix="/holdings",
    tags=["Holdings"],
)

@router.get(
    "/",
    response_model=list[HoldingResponse],
)
def get_holdings(
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

    return [
        HoldingResponse(
            asset_name=asset,
            quantity=quantity,
        )
        for asset, quantity in holdings.items()
        if quantity > 0
    ]