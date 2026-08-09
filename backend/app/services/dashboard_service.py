from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.holding import HoldingResponse
from app.schemas.dashboard import (
    DashboardSummary,
    PortfolioPerformanceSummary,
    RecentTransaction,
)

from app.services.holding_service import get_holdings
from app.services.portfolio_service import get_portfolio_performance


def get_dashboard_summary(
    db: Session,
    current_user: User,
):
    # =========================================================
    # 1. TOTAL PORTFOLIOS
    # =========================================================

    total_portfolios = (
        db.query(func.count(Portfolio.id))
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .scalar()
    ) or 0

    # =========================================================
    # 2. TOTAL TRANSACTIONS
    # =========================================================

    total_transactions = (
        db.query(func.count(Transaction.id))
        .join(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .scalar()
    ) or 0

    # =========================================================
    # 3. TOTAL UNIQUE ASSETS
    # =========================================================

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

    # =========================================================
    # 4. GET ALL USER TRANSACTIONS
    # =========================================================

    transactions = (
        db.query(Transaction)
        .join(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .all()
    )

    # =========================================================
    # 5. TOTAL INVESTED
    # =========================================================

    total_invested = 0.0

    for transaction in transactions:

        transaction_value = (
            transaction.quantity * transaction.price
        )

        if transaction.transaction_type == "BUY":
            total_invested += transaction_value

        elif transaction.transaction_type == "SELL":
            total_invested -= transaction_value

    # =========================================================
    # 6. GET ALL USER PORTFOLIOS
    # =========================================================

    portfolios = (
        db.query(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .all()
    )

    # =========================================================
    # 7. GET AND COMBINE HOLDINGS FROM ALL PORTFOLIOS
    # =========================================================

    holdings_by_asset = {}

    for portfolio in portfolios:

        portfolio_holdings = get_holdings(
            db=db,
            portfolio_id=portfolio.id,
            current_user=current_user,
        )

        for holding in portfolio_holdings:

            asset = holding.asset_name.upper()

            if asset not in holdings_by_asset:
                holdings_by_asset[asset] = {
                    "quantity": 0.0,
                    "invested": 0.0,
                    "current_value": 0.0,
                }

            holdings_by_asset[asset]["quantity"] += (
                holding.quantity
            )

            holdings_by_asset[asset]["invested"] += (
                holding.invested
            )

            holdings_by_asset[asset]["current_value"] += (
                holding.current_value
            )

    # =========================================================
    # 8. BUILD COMBINED HOLDINGS
    # =========================================================

    all_holdings = []

    for asset, data in holdings_by_asset.items():

        quantity = data["quantity"]
        invested = data["invested"]
        current_value = data["current_value"]

        current_price = (
            current_value / quantity
            if quantity > 0
            else 0.0
        )

        average_buy_price = (
            invested / quantity
            if quantity > 0
            else 0.0
        )

        profit_loss = (
            current_value - invested
        )

        profit_loss_percent = (
            (profit_loss / invested) * 100
            if invested > 0
            else 0.0
        )

        all_holdings.append(
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


    # =========================================================
    # 8. CURRENT VALUE
    # =========================================================

    current_value = sum(
        holding.current_value
        for holding in all_holdings
    )

    # =========================================================
    # 9. PROFIT / LOSS
    # =========================================================

    profit_loss = (
        current_value - total_invested
    )

    # =========================================================
    # 10. PROFIT / LOSS %
    # =========================================================

    profit_loss_percent = (
        (profit_loss / total_invested) * 100
        if total_invested > 0
        else 0.0
    )

    # =========================================================
    # 11. RECENT TRANSACTIONS
    # =========================================================

    recent_transactions = (
        db.query(Transaction)
        .join(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .order_by(
            Transaction.transaction_date.desc()
        )
        .limit(5)
        .all()
    )

    recent_transaction_response = [
        RecentTransaction.model_validate(transaction)
        for transaction in recent_transactions
    ]

    # =========================================================
    # 12. RETURN DASHBOARD
    # =========================================================

    return DashboardSummary(
        total_portfolios=total_portfolios,
        total_transactions=total_transactions,
        total_assets=total_assets,

        total_invested=total_invested,
        current_value=current_value,
        profit_loss=profit_loss,
        profit_loss_percent=profit_loss_percent,

        holdings=all_holdings,
        recent_transactions=recent_transaction_response,
    )


def get_portfolio_performance_summary(
    db: Session,
    current_user: User,
):
    # =========================================================
    # GET ALL USER PORTFOLIOS
    # =========================================================

    portfolios = (
        db.query(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .all()
    )

    result = []

    # =========================================================
    # CALCULATE PERFORMANCE FOR EACH PORTFOLIO
    # =========================================================

    for portfolio in portfolios:

        performance = get_portfolio_performance(
            db=db,
            portfolio_id=portfolio.id,
            current_user=current_user,
        )

        result.append(
            PortfolioPerformanceSummary(
                portfolio_id=portfolio.id,
                portfolio_name=portfolio.name,

                invested=performance.invested,
                current_value=performance.current_value,
                profit_loss=performance.profit_loss,
                profit_loss_percent=performance.profit_loss_percent,
            )
        )

    return result
