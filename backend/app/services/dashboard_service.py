from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.dashboard import (
    DashboardSummary,
    PortfolioPerformanceSummary,
    RecentTransaction,
)
from app.schemas.holding import HoldingResponse
from app.services.market_service import get_current_price
from app.services.portfolio_calculation_service import calculate_holdings
from app.services.portfolio_service import get_portfolio_performance


def get_dashboard_summary(
    db: Session,
    current_user: User,
) -> DashboardSummary:
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
        .order_by(
            Transaction.transaction_date,
            Transaction.id,
        )
        .all()
    )

    # =========================================================
    # 5. GET ALL USER PORTFOLIOS
    # =========================================================

    portfolios = (
        db.query(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .all()
    )

    # =========================================================
    # 6. GROUP TRANSACTIONS BY PORTFOLIO
    # =========================================================

    transactions_by_portfolio: dict[
        int,
        list[Transaction],
    ] = {}

    for transaction in transactions:

        portfolio_id = transaction.portfolio_id

        transactions_by_portfolio.setdefault(
            portfolio_id,
            [],
        ).append(transaction)

    # =========================================================
    # 7. CALCULATE AND COMBINE HOLDINGS
    # =========================================================

    holdings_by_asset: dict[
        str,
        dict[str, float],
    ] = {}

    for portfolio in portfolios:

        portfolio_transactions = (
            transactions_by_portfolio.get(
                portfolio.id,
                [],
            )
        )

        portfolio_holdings = calculate_holdings(
            portfolio_transactions
        )

        for asset, data in portfolio_holdings.items():

            quantity = data["quantity"]
            invested = data["invested"]

            current_price = get_current_price(asset)

            current_value = (
                quantity * current_price
            )

            if asset not in holdings_by_asset:

                holdings_by_asset[asset] = {
                    "quantity": 0.0,
                    "invested": 0.0,
                    "current_value": 0.0,
                }

            holdings_by_asset[asset]["quantity"] += (
                quantity
            )

            holdings_by_asset[asset]["invested"] += (
                invested
            )

            holdings_by_asset[asset]["current_value"] += (
                current_value
            )

    # =========================================================
    # 8. BUILD COMBINED HOLDINGS
    # =========================================================

    all_holdings: list[HoldingResponse] = []

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
    # 9. TOTAL INVESTED
    # =========================================================

    total_invested = sum(
        holding.invested
        for holding in all_holdings
    )

    # =========================================================
    # 10. CURRENT VALUE
    # =========================================================

    current_value = sum(
        holding.current_value
        for holding in all_holdings
    )

    # =========================================================
    # 11. PROFIT / LOSS
    # =========================================================

    profit_loss = (
        current_value - total_invested
    )

    # =========================================================
    # 12. PROFIT / LOSS %
    # =========================================================

    profit_loss_percent = (
        (profit_loss / total_invested) * 100
        if total_invested > 0
        else 0.0
    )

    # =========================================================
    # 13. RECENT TRANSACTIONS
    # =========================================================

    recent_transactions = (
        db.query(Transaction)
        .join(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .order_by(
            Transaction.transaction_date.desc(),
            Transaction.id.desc(),
        )
        .limit(5)
        .all()
    )

    recent_transaction_response = [
        RecentTransaction.model_validate(transaction)
        for transaction in recent_transactions
    ]

    # =========================================================
    # 14. RETURN DASHBOARD
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
) -> list[PortfolioPerformanceSummary]:
    # =========================================================
    # 1. GET ALL USER PORTFOLIOS
    # =========================================================

    portfolios = (
        db.query(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .all()
    )

    # =========================================================
    # 2. CALCULATE PERFORMANCE FOR EACH PORTFOLIO
    # =========================================================

    result: list[PortfolioPerformanceSummary] = []

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