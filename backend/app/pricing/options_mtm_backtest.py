from dataclasses import dataclass
from datetime import date
from typing import Callable, Sequence

from app.pricing.options_mtm import (
    MTMBar,
    MTMSnapshot,
    calculate_mtm_snapshot,
)
from app.pricing.strategy_valuation import (
    ContractPosition,
)


@dataclass(frozen=True)
class MTMTrade:
    """
    One completed mark-to-market options trade.
    """

    entry_date: date
    exit_date: date

    entry_underlying_price: float
    exit_underlying_price: float

    entry_market_value: float
    exit_market_value: float

    pnl: float
    return_percent: float


@dataclass(frozen=True)
class MTMEquityPoint:
    """
    Portfolio equity at one historical date.
    """

    timestamp: date
    equity: float


@dataclass(frozen=True)
class MTMBacktestResult:
    """
    Complete daily mark-to-market backtest result.
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

    trades: list[MTMTrade]
    equity_curve: list[MTMEquityPoint]
    snapshots: list[MTMSnapshot]


def _validate_initial_capital(
    initial_capital: float,
) -> None:
    if initial_capital <= 0:
        raise ValueError(
            "Initial capital must be greater than zero."
        )


def _validate_bars(
    bars: Sequence[MTMBar],
) -> None:
    if not bars:
        raise ValueError(
            "At least one MTM bar is required."
        )

    previous_timestamp: date | None = None

    for bar in bars:
        if bar.underlying_price <= 0:
            raise ValueError(
                "Underlying price must be greater than zero."
            )

        if (
            previous_timestamp is not None
            and bar.timestamp <= previous_timestamp
        ):
            raise ValueError(
                "MTM bars must be strictly chronological."
            )

        previous_timestamp = bar.timestamp


def _calculate_return_percent(
    pnl: float,
    capital: float,
) -> float:
    if capital == 0:
        return 0.0

    return (
        pnl / capital
    ) * 100.0


def _calculate_max_drawdown(
    equity_curve: Sequence[MTMEquityPoint],
) -> tuple[float, float]:

    if not equity_curve:
        return 0.0, 0.0

    peak_equity = equity_curve[0].equity

    max_drawdown = 0.0
    max_drawdown_percent = 0.0

    for point in equity_curve:
        equity = point.equity

        if equity > peak_equity:
            peak_equity = equity

        drawdown = (
            peak_equity - equity
        )

        if drawdown > max_drawdown:
            max_drawdown = drawdown

        if peak_equity > 0:
            drawdown_percent = (
                drawdown
                / peak_equity
            ) * 100.0
        else:
            drawdown_percent = 0.0

        if (
            drawdown_percent
            > max_drawdown_percent
        ):
            max_drawdown_percent = (
                drawdown_percent
            )

    return (
        max_drawdown,
        max_drawdown_percent,
    )


def _build_equity_curve(
    initial_capital: float,
    trades: Sequence[MTMTrade],
) -> list[MTMEquityPoint]:

    equity = initial_capital

    curve: list[MTMEquityPoint] = []

    for trade in trades:
        equity += trade.pnl

        curve.append(
            MTMEquityPoint(
                timestamp=trade.exit_date,
                equity=equity,
            )
        )

    return curve


def _build_trade(
    entry_snapshot: MTMSnapshot,
    exit_snapshot: MTMSnapshot,
    capital: float,
) -> MTMTrade:

    pnl = (
        exit_snapshot.pnl
        - entry_snapshot.pnl
    )

    return MTMTrade(
        entry_date=entry_snapshot.timestamp,
        exit_date=exit_snapshot.timestamp,
        entry_underlying_price=(
            entry_snapshot.underlying_price
        ),
        exit_underlying_price=(
            exit_snapshot.underlying_price
        ),
        entry_market_value=(
            entry_snapshot.market_value
        ),
        exit_market_value=(
            exit_snapshot.market_value
        ),
        pnl=pnl,
        return_percent=_calculate_return_percent(
            pnl,
            capital,
        ),
    )


def run_mtm_backtest(
    positions: list[ContractPosition],
    bars: Sequence[MTMBar],
    initial_capital: float,
    entry_signal: Callable[
        [MTMBar],
        bool,
    ],
    exit_signal: Callable[
        [MTMBar],
        bool,
    ],
) -> MTMBacktestResult:
    """
    Run a daily mark-to-market options backtest.

    Rules:

    - only one open position at a time
    - entry_signal opens the position
    - exit_signal closes the position
    - an open position is closed on the final bar
    - strategy value is calculated every day
    """

    if not positions:
        raise ValueError(
            "At least one position is required."
        )

    _validate_bars(bars)

    _validate_initial_capital(
        initial_capital,
    )

    snapshots: list[MTMSnapshot] = []

    entry_snapshot: MTMSnapshot | None = None

    trades: list[MTMTrade] = []

    for bar in bars:
        snapshot = calculate_mtm_snapshot(
            positions=positions,
            bar=bar,
        )

        snapshots.append(snapshot)

        if entry_snapshot is None:
            if entry_signal(bar):
                entry_snapshot = snapshot

            continue

        if exit_signal(bar):
            trade = _build_trade(
                entry_snapshot=entry_snapshot,
                exit_snapshot=snapshot,
                capital=initial_capital,
            )

            trades.append(trade)

            entry_snapshot = None

    if entry_snapshot is not None:
        final_snapshot = snapshots[-1]

        if (
            final_snapshot.timestamp
            > entry_snapshot.timestamp
        ):
            trade = _build_trade(
                entry_snapshot=entry_snapshot,
                exit_snapshot=final_snapshot,
                capital=initial_capital,
            )

            trades.append(trade)

    final_capital = (
        initial_capital
        + sum(
            trade.pnl
            for trade in trades
        )
    )

    total_pnl = (
        final_capital
        - initial_capital
    )

    total_return_percent = (
        _calculate_return_percent(
            total_pnl,
            initial_capital,
        )
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
            winning_trades
            / total_trades
        ) * 100.0
    else:
        win_rate_percent = 0.0

    equity_curve = _build_equity_curve(
        initial_capital,
        trades,
    )

    max_drawdown, max_drawdown_percent = (
        _calculate_max_drawdown(
            equity_curve,
        )
    )

    return MTMBacktestResult(
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
        snapshots=snapshots,
    )