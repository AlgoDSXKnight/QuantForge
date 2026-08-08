from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.models.transaction import Transaction
from app.models.user import User
from app.services.market_service import get_current_price


def get_holdings(
    db: Session,
    current_user: User,
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
            holdings[asset] = {
                "quantity": 0,
                "invested_amount": 0,
            }

        if transaction.transaction_type == "BUY":
            holdings[asset]["quantity"] += transaction.quantity
            holdings[asset]["invested_amount"] += (
                transaction.quantity * transaction.price
            )
        else:
            holdings[asset]["quantity"] -= transaction.quantity

            holdings[asset]["invested_amount"] -= (
                transaction.quantity * transaction.price
            )

    result = []

    for asset, data in holdings.items():
        quantity = data["quantity"]
        invested_amount = data["invested_amount"]

        if quantity <= 0:
            continue

        current_price = get_current_price(asset)

        current_value = quantity * current_price

        profit_loss = current_value - invested_amount

        profit_loss_percent = (
            (profit_loss / invested_amount) * 100
            if invested_amount > 0
            else 0
        )

        result.append(
            {
                "asset_name": asset,
                "quantity": quantity,
                "average_buy_price": (
                    invested_amount / quantity
                    if quantity > 0
                    else 0
                ),
                "invested_amount": invested_amount,
                "current_price": current_price,
                "current_value": current_value,
                "profit_loss": profit_loss,
                "profit_loss_percent": profit_loss_percent,
            }
        )

    return result

