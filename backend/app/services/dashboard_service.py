from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.dashboard import DashboardSummary


def get_dashboard_summary(
    db: Session,
    current_user: User,
):
    total_portfolios = (
        db.query(func.count(Portfolio.id))
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .scalar()
    ) or 0

    total_transactions = (
        db.query(func.count(Transaction.id))
        .join(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .scalar()
    ) or 0

    total_assets = (
        db.query(
            func.count(
                func.distinct(Transaction.asset_name)
            )
        )
        .join(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .scalar()
    ) or 0

    transactions = (
        db.query(Transaction)
        .join(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .all()
    )

    total_invested = 0

    for transaction in transactions:
        if transaction.transaction_type == "BUY":
            total_invested += (
                transaction.quantity * transaction.price
            )
        else:
            total_invested -= (
                transaction.quantity * transaction.price
            )

    return DashboardSummary(
        total_portfolios=total_portfolios,
        total_transactions=total_transactions,
        total_assets=total_assets,
        total_invested=total_invested,
    )

