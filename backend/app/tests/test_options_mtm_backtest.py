from datetime import date

import pytest

from app.pricing.option_contract import OptionContract
from app.pricing.options_mtm import MTMBar
from app.pricing.options_mtm_backtest import (
    MTMBacktestResult,
    MTMTrade,
    run_mtm_backtest,
)
from app.pricing.strategy_valuation import (
    ContractPosition,
)


def create_position() -> ContractPosition:
    contract = OptionContract(
        underlying="INFY",
        option_type="CALL",
        strike=100.0,
        expiration=date(2026, 12, 31),
        volatility=0.20,
        risk_free_rate=0.05,
    )

    return ContractPosition(
        contract=contract,
        quantity=1,
        premium=10.0,
    )


def create_bars() -> list[MTMBar]:
    return [
        MTMBar(
            timestamp=date(2026, 6, 1),
            underlying_price=100.0,
        ),
        MTMBar(
            timestamp=date(2026, 6, 2),
            underlying_price=105.0,
        ),
        MTMBar(
            timestamp=date(2026, 6, 3),
            underlying_price=110.0,
        ),
        MTMBar(
            timestamp=date(2026, 6, 4),
            underlying_price=115.0,
        ),
    ]


def test_run_mtm_backtest() -> None:
    position = create_position()

    result = run_mtm_backtest(
        positions=[position],
        bars=create_bars(),
        initial_capital=1000.0,
        entry_signal=lambda bar: (
            bar.timestamp == date(2026, 6, 1)
        ),
        exit_signal=lambda bar: (
            bar.timestamp == date(2026, 6, 3)
        ),
    )

    assert isinstance(
        result,
        MTMBacktestResult,
    )

    assert len(result.trades) == 1

    assert result.trades[0].entry_date == date(
        2026,
        6,
        1,
    )

    assert result.trades[0].exit_date == date(
        2026,
        6,
        3,
    )

    assert result.trades[0].pnl != 0.0


def test_mtm_backtest_creates_daily_snapshots() -> None:
    position = create_position()

    result = run_mtm_backtest(
        positions=[position],
        bars=create_bars(),
        initial_capital=1000.0,
        entry_signal=lambda bar: True,
        exit_signal=lambda bar: False,
    )

    assert len(result.snapshots) == 4

    assert result.snapshots[0].timestamp == date(
        2026,
        6,
        1,
    )

    assert result.snapshots[-1].timestamp == date(
        2026,
        6,
        4,
    )


def test_mtm_backtest_closes_on_final_bar() -> None:
    position = create_position()

    result = run_mtm_backtest(
        positions=[position],
        bars=create_bars(),
        initial_capital=1000.0,
        entry_signal=lambda bar: (
            bar.timestamp == date(2026, 6, 1)
        ),
        exit_signal=lambda bar: False,
    )

    assert len(result.trades) == 1

    assert result.trades[0].exit_date == date(
        2026,
        6,
        4,
    )


def test_mtm_backtest_equity_curve() -> None:
    position = create_position()

    result = run_mtm_backtest(
        positions=[position],
        bars=create_bars(),
        initial_capital=1000.0,
        entry_signal=lambda bar: (
            bar.timestamp == date(2026, 6, 1)
        ),
        exit_signal=lambda bar: (
            bar.timestamp == date(2026, 6, 3)
        ),
    )

    assert len(
        result.equity_curve
    ) == 1

    assert (
        result.equity_curve[0].equity
        == result.final_capital
    )


def test_mtm_backtest_win_statistics() -> None:
    position = create_position()

    result = run_mtm_backtest(
        positions=[position],
        bars=create_bars(),
        initial_capital=1000.0,
        entry_signal=lambda bar: (
            bar.timestamp == date(2026, 6, 1)
        ),
        exit_signal=lambda bar: (
            bar.timestamp == date(2026, 6, 3)
        ),
    )

    assert result.winning_trades == 1
    assert result.losing_trades == 0
    assert result.win_rate_percent == 100.0


def test_mtm_backtest_requires_positions() -> None:
    with pytest.raises(
        ValueError,
        match="At least one position",
    ):
        run_mtm_backtest(
            positions=[],
            bars=create_bars(),
            initial_capital=1000.0,
            entry_signal=lambda bar: True,
            exit_signal=lambda bar: True,
        )


def test_mtm_backtest_requires_bars() -> None:
    position = create_position()

    with pytest.raises(
        ValueError,
        match="At least one MTM bar",
    ):
        run_mtm_backtest(
            positions=[position],
            bars=[],
            initial_capital=1000.0,
            entry_signal=lambda bar: True,
            exit_signal=lambda bar: True,
        )


def test_mtm_backtest_rejects_invalid_capital() -> None:
    position = create_position()

    with pytest.raises(
        ValueError,
        match="Initial capital",
    ):
        run_mtm_backtest(
            positions=[position],
            bars=create_bars(),
            initial_capital=0.0,
            entry_signal=lambda bar: True,
            exit_signal=lambda bar: True,
        )