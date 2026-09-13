from dataclasses import dataclass
from datetime import date
from typing import Callable, Sequence

from app.pricing.options_strategy import (
    OptionLeg,
    calculate_strategy_pnl,
)


@dataclass(frozen=True)
class BacktestBar:
    """
    One historical market observation.
    """

    timestamp: date
    underlying_price: float


@dataclass(frozen=True)
class BacktestTrade:
    """
    One completed strategy trade.
    """

    entry_date: date
    exit_date: date
    entry_price: float
    exit_price: float
    entry_pnl: float
    exit_pnl: float
    pnl: float
    return_percent: float


@dataclass(frozen=True)
class EquityPoint:
    """
    Portfolio equity at one point in time.
    """

    timestamp: date
    equity: float


@dataclass(frozen=True)
class BacktestResult:
    """
    Complete backtest output.
    """

    initial_capital: float
    final_capital: float
    total_pnl: float
    total_return_percent: float
    winning_trades: int
    losing_trades: int
    win_rate_percent: float
    max_drawdown: float
    max_drawdown_percent: float
    trades: list[BacktestTrade]
    equity_curve: list[EquityPoint]


def _validate_price(price: float) -> None:
    if price < 0:
        raise ValueError(
            "Underlying price cannot be negative."
        )


def _validate_bars(
    bars: Sequence[BacktestBar],
) -> None:
    if not bars:
        raise ValueError(
            "At least one historical bar is required."
        )

    previous_timestamp: date | None = None

    for bar in bars:
        _validate_price(bar.underlying_price)

        if (
            previous_timestamp is not None
            and bar.timestamp <= previous_timestamp
        ):
            raise ValueError(
                "Historical bars must be strictly chronological."
            )

        previous_timestamp = bar.timestamp


def _validate_initial_capital(
    initial_capital: float,
) -> None:
    if initial_capital <= 0:
        raise ValueError(
            "Initial capital must be greater than zero."
        )


def _calculate_return_percent(
    pnl: float,
    capital: float,
) -> float:
    if capital == 0:
        return 0.0

    return (pnl / capital) * 100.0


def calculate_trade_pnl(
    legs: list[OptionLeg],
    entry_price: float,
    exit_price: float,
) -> float:
    """
    Calculate the change in strategy P&L between entry and exit.

    This basic version assumes:
    - the strategy is opened at entry_price
    - the strategy is closed at exit_price
    - all legs have the same expiry
    - the strategy is evaluated using expiry-style payoff
    """

    _validate_price(entry_price)
    _validate_price(exit_price)

    entry_pnl = calculate_strategy_pnl(
        legs,
        entry_price,
    )

    exit_pnl = calculate_strategy_pnl(
        legs,
        exit_price,
    )

    return exit_pnl - entry_pnl


def calculate_trade(
    legs: list[OptionLeg],
    entry_date: date,
    exit_date: date,
    entry_price: float,
    exit_price: float,
    capital: float,
) -> BacktestTrade:
    """
    Build one completed backtest trade.
    """

    if exit_date <= entry_date:
        raise ValueError(
            "Exit date must be after entry date."
        )

    _validate_price(entry_price)
    _validate_price(exit_price)
    _validate_initial_capital(capital)

    entry_pnl = calculate_strategy_pnl(
        legs,
        entry_price,
    )

    exit_pnl = calculate_strategy_pnl(
        legs,
        exit_price,
    )

    pnl = exit_pnl - entry_pnl

    return_percent = _calculate_return_percent(
        pnl,
        capital,
    )

    return BacktestTrade(
        entry_date=entry_date,
        exit_date=exit_date,
        entry_price=entry_price,
        exit_price=exit_price,
        entry_pnl=entry_pnl,
        exit_pnl=exit_pnl,
        pnl=pnl,
        return_percent=return_percent,
    )


def calculate_equity_curve(
    initial_capital: float,
    trades: Sequence[BacktestTrade],
) -> list[EquityPoint]:
    """
    Build equity curve from completed trades.
    """

    _validate_initial_capital(
        initial_capital,
    )

    equity = initial_capital
    curve: list[EquityPoint] = []

    for trade in trades:
        equity += trade.pnl

        curve.append(
            EquityPoint(
                timestamp=trade.exit_date,
                equity=equity,
            )
        )

    return curve


def calculate_max_drawdown(
    equity_curve: Sequence[EquityPoint],
) -> tuple[float, float]:
    """
    Return:

    (
        maximum drawdown in currency,
        maximum drawdown in percentage
    )
    """

    if not equity_curve:
        return 0.0, 0.0

    peak_equity = equity_curve[0].equity
    max_drawdown = 0.0
    max_drawdown_percent = 0.0

    for point in equity_curve:
        equity = point.equity

        if equity > peak_equity:
            peak_equity = equity

        drawdown = peak_equity - equity

        if drawdown > max_drawdown:
            max_drawdown = drawdown

        if peak_equity > 0:
            drawdown_percent = (
                drawdown / peak_equity
            ) * 100.0
        else:
            drawdown_percent = 0.0

        if drawdown_percent > max_drawdown_percent:
            max_drawdown_percent = drawdown_percent

    return (
        max_drawdown,
        max_drawdown_percent,
    )


def run_backtest(
    legs: list[OptionLeg],
    bars: Sequence[BacktestBar],
    initial_capital: float,
    entry_signal: Callable[
        [BacktestBar],
        bool,
    ],
    exit_signal: Callable[
        [BacktestBar],
        bool,
    ],
) -> BacktestResult:
    """
    Run a basic single-position backtest.

    Rules:
    - only one open position at a time
    - entry_signal opens a trade
    - exit_signal closes a trade
    - any open trade is closed on the final bar
    """

    if not legs:
        raise ValueError(
            "At least one option leg is required."
        )

    _validate_bars(bars)

    _validate_initial_capital(
        initial_capital,
    )

    trades: list[BacktestTrade] = []

    entry_bar: BacktestBar | None = None

    for bar in bars:
        if entry_bar is None:
            if entry_signal(bar):
                entry_bar = bar

            continue

        if exit_signal(bar):
            trade = calculate_trade(
                legs=legs,
                entry_date=entry_bar.timestamp,
                exit_date=bar.timestamp,
                entry_price=entry_bar.underlying_price,
                exit_price=bar.underlying_price,
                capital=initial_capital,
            )

            trades.append(trade)
            entry_bar = None

    if entry_bar is not None:
        final_bar = bars[-1]

        if final_bar.timestamp > entry_bar.timestamp:
            trade = calculate_trade(
                legs=legs,
                entry_date=entry_bar.timestamp,
                exit_date=final_bar.timestamp,
                entry_price=entry_bar.underlying_price,
                exit_price=final_bar.underlying_price,
                capital=initial_capital,
            )

            trades.append(trade)

    final_capital = initial_capital + sum(
        trade.pnl
        for trade in trades
    )

    total_pnl = final_capital - initial_capital

    total_return_percent = _calculate_return_percent(
        total_pnl,
        initial_capital,
    )

    winning_trades = sum(
        1
        for trade in trades
        if trade.pnl > 0
    )

    losing_trades = sum(
        1
        for trade in trades
        if trade.pnl < 0
    )

    total_trades = len(trades)

    if total_trades > 0:
        win_rate_percent = (
            winning_trades / total_trades
        ) * 100.0
    else:
        win_rate_percent = 0.0

    equity_curve = calculate_equity_curve(
        initial_capital,
        trades,
    )

    max_drawdown, max_drawdown_percent = (
        calculate_max_drawdown(
            equity_curve,
        )
    )

    return BacktestResult(
        initial_capital=initial_capital,
        final_capital=final_capital,
        total_pnl=total_pnl,
        total_return_percent=total_return_percent,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        win_rate_percent=win_rate_percent,
        max_drawdown=max_drawdown,
        max_drawdown_percent=max_drawdown_percent,
        trades=trades,
        equity_curve=equity_curve,
    )