from sqlalchemy.orm import Session

from app.core.exceptions import QuantForgeException
from app.models.portfolio import Portfolio
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.portfolio import (
    AssetAllocation,
    PortfolioCreate,
    PortfolioHistory,
    PortfolioPerformance,
    PortfolioSummary,
    PortfolioUpdate,
    PortfolioHolding,
)
from app.schemas.dashboard import PortfolioPerformanceSummary
from app.services.market_service import get_current_price
from app.services.portfolio_calculation_service import (
    calculate_holdings,
    calculate_portfolio_totals,
)


def _get_user_portfolio(
    db: Session,
    portfolio_id: int,
    current_user: User,
) -> Portfolio:
    portfolio = db.get(
        Portfolio,
        portfolio_id,
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

    return portfolio


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
        raise QuantForgeException(
            message="Portfolio not found",
            status_code=404,
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
        raise QuantForgeException(
            message="Portfolio not found",
            status_code=404,
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
        raise QuantForgeException(
            message="Portfolio not found",
            status_code=404,
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
    portfolio = _get_user_portfolio(
        db=db,
        portfolio_id=portfolio_id,
        current_user=current_user,
    )

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.portfolio_id == portfolio_id,
        )
        .order_by(
            Transaction.transaction_date,
            Transaction.id,
        )
        .all()
    )

    holdings = calculate_holdings(transactions)

    total_transactions = len(transactions)

    totals = calculate_portfolio_totals(holdings)

    return PortfolioSummary(
        portfolio_name=portfolio.name,
        total_transactions=total_transactions,
        total_holdings=len(holdings),
        total_quantity=totals["total_quantity"],
        total_invested=totals["total_invested"],
    )


def get_portfolio_holdings(
    db: Session,
    portfolio_id: int,
    current_user: User,
):
    portfolio = _get_user_portfolio(
        db=db,
        portfolio_id=portfolio_id,
        current_user=current_user,
    )

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.portfolio_id == portfolio_id,
        )
        .order_by(
            Transaction.transaction_date,
            Transaction.id,
        )
        .all()
    )

    holdings = calculate_holdings(transactions)

    result = []

    for asset, data in holdings.items():
        result.append(
            PortfolioHolding(
                asset_name=asset,
                quantity=data["quantity"],
                invested=data["invested"],
            )
        )

    return result


def get_portfolio_performance(
    db: Session,
    portfolio_id: int,
    current_user: User,
):
    portfolio = _get_user_portfolio(
        db=db,
        portfolio_id=portfolio_id,
        current_user=current_user,
    )

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.portfolio_id == portfolio_id,
        )
        .order_by(
            Transaction.transaction_date,
            Transaction.id,
        )
        .all()
    )

    holdings = calculate_holdings(transactions)

    invested = 0.0
    current_value = 0.0

    for asset, data in holdings.items():
        quantity = data["quantity"]
        asset_invested = data["invested"]

        if quantity <= 0:
            continue

        invested += asset_invested

        current_price = get_current_price(asset)

        current_value += quantity * current_price

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


def get_portfolio_performance_summary(
    db: Session,
    current_user: User,
) -> list[PortfolioPerformanceSummary]:
    portfolios = (
        db.query(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .all()
    )

    transactions = (
        db.query(Transaction)
        .join(Portfolio)
        .filter(
            Portfolio.user_id == current_user.id,
        )
        .order_by(
            Transaction.transaction_date,
            Transaction.id,
        )
        .all()
    )

    transactions_by_portfolio: dict[
        int,
        list[Transaction],
    ] = {}

    for transaction in transactions:
        portfolio_id = transaction.portfolio_id

        transactions_by_portfolio.setdefault(
            portfolio_id,
            [],
        ).append(transaction)

    result: list[PortfolioPerformanceSummary] = []

    for portfolio in portfolios:
        portfolio_transactions = transactions_by_portfolio.get(
            portfolio.id,
            [],
        )

        holdings = calculate_holdings(
            portfolio_transactions
        )

        invested = 0.0
        current_value = 0.0

        for asset, data in holdings.items():
            quantity = data["quantity"]
            asset_invested = data["invested"]

            if quantity <= 0:
                continue

            invested += asset_invested

            current_price = get_current_price(asset)

            current_value += (
                quantity * current_price
            )

        profit_loss = current_value - invested

        profit_loss_percent = (
            (profit_loss / invested) * 100
            if invested > 0
            else 0.0
        )

        result.append(
            PortfolioPerformanceSummary(
                portfolio_id=portfolio.id,
                portfolio_name=portfolio.name,
                invested=invested,
                current_value=current_value,
                profit_loss=profit_loss,
                profit_loss_percent=profit_loss_percent,
            )
        )

    return result


def get_portfolio_allocation(
    db: Session,
    portfolio_id: int,
    current_user: User,
):
    _get_user_portfolio(
        db=db,
        portfolio_id=portfolio_id,
        current_user=current_user,
    )

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.portfolio_id == portfolio_id,
        )
        .all()
    )

    holdings = calculate_holdings(transactions)

    values = {}
    total_value = 0

    for asset, data in holdings.items():
        quantity = data["quantity"]

        if quantity <= 0:
            continue

        asset = asset.upper()

        current_price = get_current_price(asset)

        value = quantity * current_price

        values[asset] = value
        total_value += value

    allocation = []

    for asset, value in values.items():
        allocation.append(
            AssetAllocation(
                asset_name=asset,
                current_value=value,
                allocation_percent=(
                    value / total_value * 100
                    if total_value > 0
                    else 0
                ),
            )
        )

    return allocation


def get_portfolio_history(
    db: Session,
    portfolio_id: int,
    current_user: User,
):
    _get_user_portfolio(
        db=db,
        portfolio_id=portfolio_id,
        current_user=current_user,
    )

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.portfolio_id == portfolio_id,
        )
        .order_by(
            Transaction.transaction_date,
            Transaction.id,
        )
        .all()
    )

    history = []

    invested = 0

    for transaction in transactions:
        transaction_value = (
            transaction.quantity * transaction.price
        )

        transaction_type = (
            transaction.transaction_type.upper()
        )

        if transaction_type == "BUY":
            invested += transaction_value

        elif transaction_type == "SELL":
            invested -= transaction_value

        history.append(
            PortfolioHistory(
                date=str(transaction.transaction_date),
                invested=invested,
                current_value=invested,
            )
        )

    return history