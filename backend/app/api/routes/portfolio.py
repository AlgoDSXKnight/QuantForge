from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.portfolio import PortfolioPerformance
from app.services.portfolio_service import get_portfolio_performance
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
    PortfolioSummary,
)

from app.services.portfolio_service import (
    create_portfolio,
    get_portfolios,
    get_portfolio,
    update_portfolio,
    delete_portfolio,
    get_portfolio_summary,
    get_portfolio_performance,
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