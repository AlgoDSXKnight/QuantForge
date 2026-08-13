from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.portfolio import (
    AssetAllocation,
    PortfolioCreate,
    PortfolioHistory,
    PortfolioHolding,
    PortfolioPerformance,
    PortfolioResponse,
    PortfolioSummary,
    PortfolioUpdate,
)
from app.services.portfolio_service import (
    create_portfolio,
    delete_portfolio,
    get_portfolio,
    get_portfolio_allocation,
    get_portfolio_history,
    get_portfolio_holdings,
    get_portfolio_performance,
    get_portfolio_summary,
    get_portfolios,
    update_portfolio,
)


router = APIRouter(
    prefix="/portfolios",
    tags=["Portfolios"],
)


@router.post(
    "/",
    response_model=PortfolioResponse,
)
def create_portfolio_route(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_portfolio(
        db=db,
        portfolio_data=portfolio,
        current_user=current_user,
    )


@router.get(
    "/",
    response_model=list[PortfolioResponse],
)
def get_portfolios_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_portfolios(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/{portfolio_id}/summary",
    response_model=PortfolioSummary,
)
def get_portfolio_summary_route(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_portfolio_summary(
        db=db,
        portfolio_id=portfolio_id,
        current_user=current_user,
    )


@router.get(
    "/{portfolio_id}/holdings",
    response_model=list[PortfolioHolding],
)
def get_portfolio_holdings_route(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_portfolio_holdings(
        db=db,
        portfolio_id=portfolio_id,
        current_user=current_user,
    )


@router.get(
    "/{portfolio_id}/performance",
    response_model=PortfolioPerformance,
)
def get_portfolio_performance_route(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_portfolio_performance(
        db=db,
        portfolio_id=portfolio_id,
        current_user=current_user,
    )


@router.get(
    "/{portfolio_id}/allocation",
    response_model=list[AssetAllocation],
)
def get_portfolio_allocation_route(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_portfolio_allocation(
        db=db,
        portfolio_id=portfolio_id,
        current_user=current_user,
    )


@router.get(
    "/{portfolio_id}/history",
    response_model=list[PortfolioHistory],
)
def get_portfolio_history_route(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_portfolio_history(
        db=db,
        portfolio_id=portfolio_id,
        current_user=current_user,
    )


@router.get(
    "/{portfolio_id}",
    response_model=PortfolioResponse,
)
def get_portfolio_route(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_portfolio(
        db=db,
        portfolio_id=portfolio_id,
        current_user=current_user,
    )


@router.put(
    "/{portfolio_id}",
    response_model=PortfolioResponse,
)
def update_portfolio_route(
    portfolio_id: int,
    portfolio_data: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_portfolio(
        db=db,
        portfolio_id=portfolio_id,
        portfolio_data=portfolio_data,
        current_user=current_user,
    )


@router.delete(
    "/{portfolio_id}",
)
def delete_portfolio_route(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_portfolio(
        db=db,
        portfolio_id=portfolio_id,
        current_user=current_user,
    )