from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

from app.pricing.options_strategy import (
    long_call_butterfly,
    long_straddle,
    long_put_butterfly,
)

from app.pricing.strategy_visualization import (
    plot_strategy_payoff,
    plot_strategy_pnl,
)


def test_plot_strategy_payoff_returns_figure() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    figure = plot_strategy_payoff(
        legs=legs,
        underlying_prices=[
            80.0,
            90.0,
            100.0,
            110.0,
            120.0,
        ],
    )

    assert figure is not None
    assert len(figure.axes) == 1

    plt.close(figure)


def test_plot_strategy_pnl_returns_figure() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    figure = plot_strategy_pnl(
        legs=legs,
        underlying_prices=[
            80.0,
            90.0,
            100.0,
            110.0,
            120.0,
        ],
    )

    assert figure is not None
    assert len(figure.axes) == 1

    plt.close(figure)


def test_plot_strategy_payoff_saves_file(
    tmp_path: Path,
) -> None:
    legs = long_call_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=10.0,
        middle_premium=5.0,
        upper_premium=2.0,
    )

    output_path = (
        tmp_path
        / "strategy_payoff.png"
    )

    figure = plot_strategy_payoff(
        legs=legs,
        underlying_prices=[
            80.0,
            90.0,
            100.0,
            110.0,
            120.0,
        ],
        output_path=output_path,
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0

    plt.close(figure)


def test_plot_strategy_pnl_saves_file(
    tmp_path: Path,
) -> None:
    legs = long_put_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=6.0,
        middle_premium=10.0,
        upper_premium=15.0,
    )

    output_path = (
        tmp_path
        / "strategy_pnl.png"
    )

    figure = plot_strategy_pnl(
        legs=legs,
        underlying_prices=[
            80.0,
            90.0,
            100.0,
            110.0,
            120.0,
        ],
        output_path=output_path,
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0

    plt.close(figure)


def test_plot_strategy_payoff_requires_legs() -> None:
    with pytest.raises(
        ValueError,
        match="At least one option leg",
    ):
        plot_strategy_payoff(
            legs=[],
            underlying_prices=[
                90.0,
                100.0,
                110.0,
            ],
        )


def test_plot_strategy_payoff_requires_prices() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    with pytest.raises(
        ValueError,
        match="At least one underlying price",
    ):
        plot_strategy_payoff(
            legs=legs,
            underlying_prices=[],
        )


def test_plot_strategy_pnl_requires_legs() -> None:
    with pytest.raises(
        ValueError,
        match="At least one option leg",
    ):
        plot_strategy_pnl(
            legs=[],
            underlying_prices=[
                90.0,
                100.0,
                110.0,
            ],
        )


def test_plot_strategy_pnl_requires_prices() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    with pytest.raises(
        ValueError,
        match="At least one underlying price",
    ):
        plot_strategy_pnl(
            legs=legs,
            underlying_prices=[],
        )