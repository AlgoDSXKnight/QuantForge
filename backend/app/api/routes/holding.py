from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.holding import HoldingResponse
from app.services.holding_service import get_holdings


router = APIRouter(
    prefix="/holdings",
    tags=["Holdings"],
)


@router.get(
    "/{portfolio_id}",
    response_model=list[HoldingResponse],
)
def get_holdings_route(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_holdings(
        db=db,
        portfolio_id=portfolio_id,
        current_user=current_user,
    )
