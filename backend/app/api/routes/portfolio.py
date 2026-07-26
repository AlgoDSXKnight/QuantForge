from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
)

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.portfolio import Portfolio
from app.models.user import User
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioResponse,
)

router = APIRouter(
    prefix="/portfolios",
    tags=["Portfolios"],
)

@router.post(
    "/",
    response_model=PortfolioResponse,
)
def create_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_portfolio = Portfolio(
        name=portfolio.name,
        user_id=current_user.id,
    )

    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)

    return new_portfolio

@router.get(
    "/",
    response_model=list[PortfolioResponse],
)
def get_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    portfolios = (
        db.query(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id
        )
        .all()
    )

    return portfolios

@router.get(
    "/{portfolio_id}",
    response_model=PortfolioResponse,
)
def get_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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

    return portfolio

@router.put(
    "/{portfolio_id}",
    response_model=PortfolioResponse,
)
def update_portfolio(
    portfolio_id: int,
    updated_portfolio: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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

    portfolio.name = updated_portfolio.name

    db.commit()
    db.refresh(portfolio)

    return portfolio

@router.delete("/{portfolio_id}")
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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

    db.delete(portfolio)
    db.commit()

    return {
        "message": "Portfolio deleted successfully"
    }