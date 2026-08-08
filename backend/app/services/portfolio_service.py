from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import QuantForgeException
from app.models.portfolio import Portfolio
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.portfolio import (
    AssetAllocation,
    PortfolioCreate,
    PortfolioHistory,
    PortfolioPerformance,
    PortfolioSummary,
    PortfolioUpdate,
)
from app.services.market_service import get_current_price


def create_portfolio(
    db: Session,
    portfolio_data: PortfolioCreate,
    current_user: User,
):
    portfolio = Portfolio(
        name=portfolio_data.name,
        user_id=current_user.id,
    )

    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)

    return portfolio


def get_portfolios(
    db: Session,
    current_user: User,
):
    return (
        db.query(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .all()
    )


def get_portfolio(
    db: Session,
    portfolio_id: int,
    current_user: User,
):
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
        )
        .first()
    )

    if portfolio is None:
        raise QuantForgeException(
            message="Portfolio not found",
            status_code=404,
        )

    return portfolio


def update_portfolio(
    db: Session,
    portfolio_id: int,
    portfolio_data: PortfolioUpdate,
    current_user: User,
):
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
        )
        .first()
    )

    if portfolio is None:
        raise QuantForgeException(
            message="Portfolio not found",
            status_code=404,
        )

    portfolio.name = portfolio_data.name

    db.commit()
    db.refresh(portfolio)

    return portfolio


def delete_portfolio(
    db: Session,
    portfolio_id: int,
    current_user: User,
):
    portfolio = (
        db.query(Portfolio)
        .filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
        )
        .first()
    )

    if portfolio is None:
        raise QuantForgeException(
            message="Portfolio not found",
            status_code=404,
        )

    db.delete(portfolio)
    db.commit()

    return {
        "message": "Portfolio deleted successfully",
    }


def get_portfolio_summary(
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

    total_transactions = (
        db.query(func.count(Transaction.id))
        .filter(
            Transaction.portfolio_id == portfolio_id,
        )
        .scalar()
    ) or 0

    total_holdings = (
        db.query(
            func.count(
                func.distinct(Transaction.asset_name)
            )
        )
        .filter(
            Transaction.portfolio_id == portfolio_id,
        )
        .scalar()
    ) or 0

    total_quantity = 0
    total_invested = 0

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.portfolio_id == portfolio_id,
        )
        .all()
    )

    for transaction in transactions:
        transaction_value = (
            transaction.quantity * transaction.price
        )

        if transaction.transaction_type == "BUY":
            total_quantity += transaction.quantity
            total_invested += transaction_value
        else:
            total_quantity -= transaction.quantity
            total_invested -= transaction_value

    return PortfolioSummary(
        portfolio_name=portfolio.name,
        total_transactions=total_transactions,
        total_holdings=total_holdings,
        total_quantity=total_quantity,
        total_invested=total_invested,
    )


def get_portfolio_performance(
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
        .all()
    )

    holdings = {}

    for transaction in transactions:
        asset = transaction.asset_name

        if asset not in holdings:
            holdings[asset] = {
                "quantity": 0,
                "invested": 0,
            }

        transaction_value = (
            transaction.quantity * transaction.price
        )

        if transaction.transaction_type == "BUY":
            holdings[asset]["quantity"] += transaction.quantity
            holdings[asset]["invested"] += transaction_value
        else:
            holdings[asset]["quantity"] -= transaction.quantity
            holdings[asset]["invested"] -= transaction_value

    invested = 0
    current_value = 0

    for asset, data in holdings.items():
        if data["quantity"] <= 0:
            continue

        invested += data["invested"]

        current_value += (
            data["quantity"]
            * get_current_price(asset)
        )

    profit_loss = current_value - invested

    profit_loss_percent = (
        (profit_loss / invested) * 100
        if invested > 0
        else 0
    )

    return PortfolioPerformance(
        portfolio_name=portfolio.name,
        invested=invested,
        current_value=current_value,
        profit_loss=profit_loss,
        profit_loss_percent=profit_loss_percent,
    )


def get_portfolio_allocation(
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

    values = {}
    total_value = 0

    for asset, quantity in holdings.items():
        if quantity <= 0:
            continue

        value = quantity * get_current_price(asset)

        values[asset] = value
        total_value += value

    allocation = []

    for asset, value in values.items():
        allocation.append(
            AssetAllocation(
                asset_name=asset,
                current_value=value,
                allocation_percent=(
                    value / total_value * 100
                    if total_value > 0
                    else 0
                ),
            )
        )

    return allocation


def get_portfolio_history(
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

    history = []

    invested = 0

    for transaction in transactions:
        transaction_value = (
            transaction.quantity * transaction.price
        )

        if transaction.transaction_type == "BUY":
            invested += transaction_value
        else:
            invested -= transaction_value

        history.append(
            PortfolioHistory(
                date=str(transaction.transaction_date),
                invested=invested,
                current_value=invested,
            )
        )

    return history

