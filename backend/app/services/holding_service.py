from sqlalchemy.orm import Session

from app.core.exceptions import QuantForgeException
from app.models.portfolio import Portfolio
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.holding import HoldingResponse
from app.services.market_service import get_current_price
from app.services.portfolio_calculation_service import calculate_holdings


def get_holdings(
    db: Session,
    portfolio_id: int,
    current_user: User,
):
    portfolio = db.get(
        Portfolio,
        portfolio_id,
    )

    if portfolio is None:
        raise QuantForgeException(
            message="Portfolio not found",
            status_code=404,
        )

    if portfolio.user_id != current_user.id:
        raise QuantForgeException(
            message="Access denied",
            status_code=403,
        )

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.portfolio_id == portfolio_id,
        )
        .order_by(Transaction.transaction_date)
        .all()
    )

    holdings = calculate_holdings(transactions)

    result = []

    for asset, data in holdings.items():
        quantity = data["quantity"]
        invested = data["invested"]

        if quantity <= 0:
            continue

        average_buy_price = (
            invested / quantity
            if quantity > 0
            else 0
        )

        current_price = get_current_price(asset)

        current_value = quantity * current_price

        profit_loss = current_value - invested

        profit_loss_percent = (
            (profit_loss / invested) * 100
            if invested > 0
            else 0
        )

        result.append(
            HoldingResponse(
                asset_name=asset,
                quantity=quantity,
                average_buy_price=average_buy_price,
                invested=invested,
                current_price=current_price,
                current_value=current_value,
                profit_loss=profit_loss,
                profit_loss_percent=profit_loss_percent,
            )
        )

    return result
