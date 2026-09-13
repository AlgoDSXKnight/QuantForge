from pathlib import Path

import matplotlib.pyplot as plt

from app.pricing.options_strategy import (
    OptionLeg,
    calculate_strategy_payoff_curve,
)


def plot_strategy_payoff(
    legs: list[OptionLeg],
    underlying_prices: list[float],
    output_path: str | Path | None = None,
):
    """
    Plot an option strategy's payoff and P&L.

    Parameters
    ----------
    legs:
        Option legs making up the strategy.

    underlying_prices:
        Underlying prices at which the strategy
        should be evaluated.

    output_path:
        Optional path where the chart should be saved.

    Returns
    -------
    matplotlib.figure.Figure
        The generated figure.
    """

    if not legs:
        raise ValueError(
            "At least one option leg is required."
        )

    if not underlying_prices:
        raise ValueError(
            "At least one underlying price is required."
        )

    curve = calculate_strategy_payoff_curve(
        legs,
        underlying_prices,
    )

    prices = [
        point.underlying_price
        for point in curve
    ]

    payoff = [
        point.payoff
        for point in curve
    ]

    pnl = [
        point.pnl
        for point in curve
    ]

    figure, axis = plt.subplots(
        figsize=(10, 6)
    )

    axis.plot(
        prices,
        payoff,
        label="Payoff",
    )

    axis.plot(
        prices,
        pnl,
        label="P&L",
    )

    axis.axhline(
        0,
        linewidth=1,
    )

    axis.set_title(
        "Option Strategy Payoff"
    )

    axis.set_xlabel(
        "Underlying Price"
    )

    axis.set_ylabel(
        "Value"
    )

    axis.grid(
        True,
        alpha=0.3,
    )

    axis.legend()

    figure.tight_layout()

    if output_path is not None:
        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        figure.savefig(
            output_path,
            dpi=150,
            bbox_inches="tight",
        )

    return figure


def plot_strategy_pnl(
    legs: list[OptionLeg],
    underlying_prices: list[float],
    output_path: str | Path | None = None,
):
    """
    Plot only the strategy P&L curve.
    """

    if not legs:
        raise ValueError(
            "At least one option leg is required."
        )

    if not underlying_prices:
        raise ValueError(
            "At least one underlying price is required."
        )

    curve = calculate_strategy_payoff_curve(
        legs,
        underlying_prices,
    )

    prices = [
        point.underlying_price
        for point in curve
    ]

    pnl = [
        point.pnl
        for point in curve
    ]

    figure, axis = plt.subplots(
        figsize=(10, 6)
    )

    axis.plot(
        prices,
        pnl,
        label="P&L",
    )

    axis.axhline(
        0,
        linewidth=1,
    )

    axis.set_title(
        "Option Strategy P&L"
    )

    axis.set_xlabel(
        "Underlying Price"
    )

    axis.set_ylabel(
        "Profit / Loss"
    )

    axis.grid(
        True,
        alpha=0.3,
    )

    axis.legend()

    figure.tight_layout()

    if output_path is not None:
        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        figure.savefig(
            output_path,
            dpi=150,
            bbox_inches="tight",
        )

    return figure