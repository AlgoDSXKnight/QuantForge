from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.portfolio import Portfolio
from app.models.user import User
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
)


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