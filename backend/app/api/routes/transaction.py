from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
)
from app.services.transaction_service import (
    create_transaction,
    get_transactions,
    get_transaction,
    update_transaction,
    delete_transaction,
)

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.post(
    "/",
    response_model=TransactionResponse,
)
def create_transaction_route(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_transaction(
        db=db,
        transaction_data=transaction,
        current_user=current_user,
    )


@router.get(
    "/",
    response_model=list[TransactionResponse],
)
def get_transactions_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_transactions(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def get_transaction_route(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_transaction(
        db=db,
        transaction_id=transaction_id,
        current_user=current_user,
    )


@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def update_transaction_route(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_transaction(
        db=db,
        transaction_id=transaction_id,
        transaction_data=transaction_data,
        current_user=current_user,
    )


@router.delete(
    "/{transaction_id}",
)
def delete_transaction_route(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_transaction(
        db=db,
        transaction_id=transaction_id,
        current_user=current_user,
    )