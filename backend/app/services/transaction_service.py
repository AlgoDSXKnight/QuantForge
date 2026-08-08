from sqlalchemy.orm import Session

from app.core.exceptions import QuantForgeException
from app.models.portfolio import Portfolio
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionCreate
from app.schemas.transaction import TransactionUpdate


def create_transaction(
    db: Session,
    transaction_data: TransactionCreate,
    current_user: User,
):
    portfolio = db.get(
        Portfolio,
        transaction_data.portfolio_id,
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

    new_transaction = Transaction(
        asset_name=transaction_data.asset_name,
        transaction_type=transaction_data.transaction_type,
        quantity=transaction_data.quantity,
        price=transaction_data.price,
        portfolio_id=transaction_data.portfolio_id,
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


def get_transaction(
    db: Session,
    transaction_id: int,
    current_user: User,
):
    transaction = (
        db.query(Transaction)
        .join(Portfolio)
        .filter(
            Transaction.id == transaction_id,
            Portfolio.user_id == current_user.id,
        )
        .first()
    )

    if transaction is None:
        raise QuantForgeException(
            message="Transaction not found",
            status_code=404,
        )

    return transaction


def get_transactions(
    db: Session,
    current_user: User,
):
    return (
        db.query(Transaction)
        .join(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .all()
    )


def update_transaction(
    db: Session,
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User,
):
    transaction = (
        db.query(Transaction)
        .join(Portfolio)
        .filter(
            Transaction.id == transaction_id,
            Portfolio.user_id == current_user.id,
        )
        .first()
    )

    if transaction is None:
        raise QuantForgeException(
            message="Transaction not found",
            status_code=404,
        )

    transaction.asset_name = transaction_data.asset_name
    transaction.transaction_type = transaction_data.transaction_type
    transaction.quantity = transaction_data.quantity
    transaction.price = transaction_data.price

    db.commit()
    db.refresh(transaction)

    return transaction


def delete_transaction(
    db: Session,
    transaction_id: int,
    current_user: User,
):
    transaction = (
        db.query(Transaction)
        .join(Portfolio)
        .filter(
            Transaction.id == transaction_id,
            Portfolio.user_id == current_user.id,
        )
        .first()
    )

    if transaction is None:
        raise QuantForgeException(
            message="Transaction not found",
            status_code=404,
        )

    db.delete(transaction)
    db.commit()

    return {
        "message": "Transaction deleted successfully",
    }
