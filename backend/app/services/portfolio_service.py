from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.portfolio import Portfolio
from app.models.user import User
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
)

from sqlalchemy import func
from app.models.transaction import Transaction
from app.schemas.portfolio import PortfolioSummary
from app.schemas.portfolio import PortfolioPerformance
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
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found",
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
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found",
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
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found",
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
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found",
        )

    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    total_transactions = (
        db.query(func.count(Transaction.id))
        .filter(
            Transaction.portfolio_id == portfolio_id,
        )
        .scalar()
    )

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

    total_quantity = (
        db.query(func.sum(Transaction.quantity))
        .filter(
            Transaction.portfolio_id == portfolio_id,
        )
        .scalar()
    ) or 0

    total_invested = (
        db.query(
            func.sum(
                Transaction.quantity * Transaction.price
            )
        )
        .filter(
            Transaction.portfolio_id == portfolio_id,
        )
        .scalar()
    ) or 0

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
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found",
        )

    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
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

        if transaction.transaction_type == "BUY":
            holdings[asset]["quantity"] += transaction.quantity
            holdings[asset]["invested"] += (
                transaction.quantity * transaction.price
            )

        else:
            holdings[asset]["quantity"] -= transaction.quantity
            holdings[asset]["invested"] -= (
                transaction.quantity * transaction.price
            )

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