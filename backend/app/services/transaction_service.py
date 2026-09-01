from sqlalchemy.orm import Session

from app.core.exceptions import QuantForgeException
from app.models.portfolio import Portfolio
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
)
from app.services.portfolio_calculation_service import calculate_holdings


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

    # For SELL transactions, validate the resulting portfolio
    # before inserting the transaction into the database.
    if transaction_data.transaction_type == "SELL":

        transactions = (
            db.query(Transaction)
            .filter(
                Transaction.portfolio_id
                == transaction_data.portfolio_id
            )
            .order_by(
                Transaction.transaction_date,
                Transaction.id,
            )
            .all()
        )

        candidate_transaction = Transaction(
            asset_name=transaction_data.asset_name,
            transaction_type=transaction_data.transaction_type,
            quantity=transaction_data.quantity,
            price=transaction_data.price,
            portfolio_id=transaction_data.portfolio_id,
        )

        transactions.append(candidate_transaction)

        try:
            calculate_holdings(transactions)

        except ValueError as exc:
            raise QuantForgeException(
                message=str(exc),
                status_code=400,
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

    # Get the complete portfolio transaction history.
    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.portfolio_id
            == transaction.portfolio_id
        )
        .order_by(
            Transaction.transaction_date,
            Transaction.id,
        )
        .all()
    )

    # Build an in-memory representation of the history
    # using the proposed transaction values.
    candidate_transactions = []

    for item in transactions:

        if item.id == transaction.id:
            candidate_transactions.append(
                {
                    "asset_name": transaction_data.asset_name,
                    "transaction_type": transaction_data.transaction_type,
                    "quantity": transaction_data.quantity,
                    "price": transaction_data.price,
                    "transaction_date": item.transaction_date,
                }
            )

        else:
            candidate_transactions.append(
                {
                    "asset_name": item.asset_name,
                    "transaction_type": item.transaction_type,
                    "quantity": item.quantity,
                    "price": item.price,
                    "transaction_date": item.transaction_date,
                }
            )

    # Create temporary Transaction-like objects for validation.
    validation_transactions = []

    for item in candidate_transactions:
        validation_transaction = Transaction(
            asset_name=item["asset_name"],
            transaction_type=item["transaction_type"],
            quantity=item["quantity"],
            price=item["price"],
            transaction_date=item["transaction_date"],
            portfolio_id=transaction.portfolio_id,
        )

        validation_transactions.append(
            validation_transaction
        )

    try:
        calculate_holdings(validation_transactions)

    except ValueError as exc:
        raise QuantForgeException(
            message=str(exc),
            status_code=400,
        )

    # Validation passed.
    # Now modify the real database object.
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

    # Get the complete transaction history.
    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.portfolio_id
            == transaction.portfolio_id
        )
        .order_by(
            Transaction.transaction_date,
            Transaction.id,
        )
        .all()
    )

    # Simulate the portfolio AFTER deleting this transaction.
    remaining_transactions = [
        item
        for item in transactions
        if item.id != transaction.id
    ]

    try:
        calculate_holdings(remaining_transactions)

    except ValueError as exc:
        db.rollback()

        raise QuantForgeException(
            message=str(exc),
            status_code=400,
        )

    # Resulting history is valid.
    db.delete(transaction)
    db.commit()

    return {
        "message": "Transaction deleted successfully",
    }