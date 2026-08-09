from collections import defaultdict

from app.models.transaction import Transaction


def calculate_holdings(
    transactions: list[Transaction],
) -> dict[str, dict[str, float]]:
    """
    Convert transactions into current holdings.

    BUY:
        quantity += bought quantity
        invested += bought quantity * buy price

    SELL:
        quantity -= sold quantity
        invested -= cost basis of sold quantity

    The SELL removes the cost basis of the shares sold,
    not the cash received from the sale.
    """

    holdings = defaultdict(
        lambda: {
            "quantity": 0.0,
            "invested": 0.0,
        }
    )

    for transaction in transactions:

        print(
    "CALC DEBUG:",
    "id=", transaction.id,
    "asset=", repr(transaction.asset_name),
    "type=", repr(transaction.transaction_type),
    "quantity=", transaction.quantity,
    "price=", transaction.price,
)
        asset = str(transaction.asset_name).strip().upper()
        transaction_type = str(
            transaction.transaction_type
        ).strip().upper()

        quantity = float(transaction.quantity)
        price = float(transaction.price)

        if quantity <= 0:
            continue

        # -------------------------
        # BUY
        # -------------------------
        if transaction_type == "BUY":
            holdings[asset]["quantity"] += quantity
            holdings[asset]["invested"] += (
                quantity * price
            )

        # -------------------------
        # SELL
        # -------------------------
        elif transaction_type == "SELL":
            current_quantity = holdings[asset]["quantity"]
            current_invested = holdings[asset]["invested"]

            if quantity > current_quantity:
                raise ValueError(
                    f"Cannot sell {quantity} shares of "
                    f"{asset}. Current holding is "
                    f"{current_quantity}."
                )

            if current_quantity > 0:
                average_cost = (
                    current_invested / current_quantity
                )

                cost_basis_sold = (
                    quantity * average_cost
                )

                holdings[asset]["quantity"] -= quantity

                holdings[asset]["invested"] -= (
                    cost_basis_sold
                )

        else:
            raise ValueError(
                f"Unsupported transaction type: "
                f"{transaction_type}"
            )

    # Convert defaultdict → normal dict.
    #
    # Also make sure every value is a normal dictionary,
    # not a tuple or SQLAlchemy Row object.
    result: dict[str, dict[str, float]] = {}

    for asset, data in holdings.items():
        quantity = float(data["quantity"])
        invested = float(data["invested"])

        # Remove completely sold positions.
        if quantity <= 0:
            continue

        result[asset] = {
            "quantity": quantity,
            "invested": invested,
        }
        
    print("CALC RESULT:", result)
    return result


def calculate_portfolio_totals(
    holdings: dict[str, dict[str, float]],
) -> dict[str, float]:
    """
    Calculate aggregate quantity and invested cost
    from already-calculated holdings.
    """

    total_quantity = 0.0
    total_invested = 0.0

    for asset, data in holdings.items():
        quantity = float(data["quantity"])
        invested = float(data["invested"])

        if quantity <= 0:
            continue

        total_quantity += quantity
        total_invested += invested

    return {
        "total_quantity": total_quantity,
        "total_invested": total_invested,
    }
