from datetime import date

import pytest

from app.pricing.options_backtesting import (
    BacktestBar,
    BacktestResult,
    BacktestTrade,
    calculate_equity_curve,
    calculate_max_drawdown,
    calculate_trade,
    calculate_trade_pnl,
    run_backtest,
)

from app.pricing.options_strategy import (
    long_call_butterfly,
    long_straddle,
)


def test_calculate_trade_pnl() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    pnl = calculate_trade_pnl(
        legs,
        entry_price=100.0,
        exit_price=120.0,
    )

    assert pnl == 20.0


def test_calculate_trade() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    trade = calculate_trade(
        legs=legs,
        entry_date=date(2026, 1, 1),
        exit_date=date(2026, 1, 10),
        entry_price=100.0,
        exit_price=120.0,
        capital=1000.0,
    )

    assert isinstance(
        trade,
        BacktestTrade,
    )

    assert trade.entry_pnl == -10.0
    assert trade.exit_pnl == 10.0
    assert trade.pnl == 20.0
    assert trade.return_percent == 2.0


def test_calculate_equity_curve() -> None:
    trades = [
        BacktestTrade(
            entry_date=date(2026, 1, 1),
            exit_date=date(2026, 1, 5),
            entry_price=100.0,
            exit_price=110.0,
            entry_pnl=-10.0,
            exit_pnl=0.0,
            pnl=10.0,
            return_percent=1.0,
        ),
        BacktestTrade(
            entry_date=date(2026, 1, 6),
            exit_date=date(2026, 1, 10),
            entry_price=110.0,
            exit_price=90.0,
            entry_pnl=0.0,
            exit_pnl=-10.0,
            pnl=-20.0,
            return_percent=-2.0,
        ),
    ]

    curve = calculate_equity_curve(
        initial_capital=1000.0,
        trades=trades,
    )

    assert curve[0].equity == 1010.0
    assert curve[1].equity == 990.0


def test_calculate_max_drawdown() -> None:
    trades = [
        BacktestTrade(
            entry_date=date(2026, 1, 1),
            exit_date=date(2026, 1, 5),
            entry_price=100.0,
            exit_price=110.0,
            entry_pnl=-10.0,
            exit_pnl=0.0,
            pnl=100.0,
            return_percent=10.0,
        ),
        BacktestTrade(
            entry_date=date(2026, 1, 6),
            exit_date=date(2026, 1, 10),
            entry_price=110.0,
            exit_price=90.0,
            entry_pnl=0.0,
            exit_pnl=-10.0,
            pnl=-50.0,
            return_percent=-5.0,
        ),
    ]

    curve = calculate_equity_curve(
        initial_capital=1000.0,
        trades=trades,
    )

    drawdown, drawdown_percent = calculate_max_drawdown(
        curve,
    )

    assert drawdown == 50.0
    assert drawdown_percent == pytest.approx(
        4.54545454545,
    )


def test_run_backtest() -> None:
    legs = long_call_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=2.0,
        middle_premium=1.0,
        upper_premium=2.0,
    )

    bars = [
        BacktestBar(
            timestamp=date(2026, 1, 1),
            underlying_price=90.0,
        ),
        BacktestBar(
            timestamp=date(2026, 1, 2),
            underlying_price=95.0,
        ),
        BacktestBar(
            timestamp=date(2026, 1, 3),
            underlying_price=100.0,
        ),
        BacktestBar(
            timestamp=date(2026, 1, 4),
            underlying_price=105.0,
        ),
        BacktestBar(
            timestamp=date(2026, 1, 5),
            underlying_price=110.0,
        ),
    ]

    result = run_backtest(
        legs=legs,
        bars=bars,
        initial_capital=1000.0,
        entry_signal=lambda bar: (
            bar.timestamp == date(2026, 1, 1)
        ),
        exit_signal=lambda bar: (
            bar.timestamp == date(2026, 1, 3)
        ),
    )

    assert isinstance(
        result,
        BacktestResult,
    )

    assert len(result.trades) == 1
    assert result.winning_trades == 1
    assert result.losing_trades == 0
    assert result.win_rate_percent == 100.0
    assert result.final_capital == 1010.0
    assert result.total_pnl == 10.0


def test_run_backtest_closes_open_trade_on_final_bar() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    bars = [
        BacktestBar(
            timestamp=date(2026, 1, 1),
            underlying_price=100.0,
        ),
        BacktestBar(
            timestamp=date(2026, 1, 2),
            underlying_price=120.0,
        ),
    ]

    result = run_backtest(
        legs=legs,
        bars=bars,
        initial_capital=1000.0,
        entry_signal=lambda bar: True,
        exit_signal=lambda bar: False,
    )

    assert len(result.trades) == 1
    assert result.total_pnl == 20.0


def test_backtest_requires_legs() -> None:
    bars = [
        BacktestBar(
            timestamp=date(2026, 1, 1),
            underlying_price=100.0,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="At least one option leg",
    ):
        run_backtest(
            legs=[],
            bars=bars,
            initial_capital=1000.0,
            entry_signal=lambda bar: True,
            exit_signal=lambda bar: True,
        )


def test_backtest_requires_bars() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    with pytest.raises(
        ValueError,
        match="At least one historical bar",
    ):
        run_backtest(
            legs=legs,
            bars=[],
            initial_capital=1000.0,
            entry_signal=lambda bar: True,
            exit_signal=lambda bar: True,
        )


def test_backtest_rejects_non_chronological_bars() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    bars = [
        BacktestBar(
            timestamp=date(2026, 1, 2),
            underlying_price=100.0,
        ),
        BacktestBar(
            timestamp=date(2026, 1, 1),
            underlying_price=110.0,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="strictly chronological",
    ):
        run_backtest(
            legs=legs,
            bars=bars,
            initial_capital=1000.0,
            entry_signal=lambda bar: True,
            exit_signal=lambda bar: True,
        )