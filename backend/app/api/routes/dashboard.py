from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User

from app.schemas.dashboard import (
    DashboardSummary,
    PortfolioPerformanceSummary,
)

from app.services.dashboard_service import (
    get_dashboard_summary,
    get_portfolio_performance_summary,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/",
    response_model=DashboardSummary,
)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_dashboard_summary(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/portfolios",
    response_model=list[PortfolioPerformanceSummary],
)
def portfolio_performance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_portfolio_performance_summary(
        db=db,
        current_user=current_user,
    )
