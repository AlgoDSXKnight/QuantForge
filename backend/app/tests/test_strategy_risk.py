from app.pricing.options_strategy import (
    long_call_butterfly,
    long_straddle,
    long_put_butterfly,
)

from app.pricing.strategy_risk import (
    ScenarioResult,
    RiskAnalysis,
    calculate_best_case_scenario,
    calculate_profit_range,
    calculate_risk_analysis,
    calculate_scenario,
    calculate_scenarios,
    calculate_worst_case_scenario,
)

import pytest


def test_calculate_scenario_profit() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    result = calculate_scenario(
        legs,
        120.0,
    )

    assert isinstance(
        result,
        ScenarioResult,
    )

    assert result.underlying_price == 120.0
    assert result.pnl == 10.0
    assert result.status == "PROFIT"


def test_calculate_scenario_loss() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    result = calculate_scenario(
        legs,
        100.0,
    )

    assert result.pnl == -10.0
    assert result.status == "LOSS"


def test_calculate_scenario_breakeven() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    result = calculate_scenario(
        legs,
        110.0,
    )

    assert result.pnl == 0.0
    assert result.status == "BREAKEVEN"


def test_calculate_scenarios() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    results = calculate_scenarios(
        legs,
        [
            80.0,
            100.0,
            120.0,
        ],
    )

    assert len(results) == 3

    assert results[0].pnl == 10.0
    assert results[1].pnl == -10.0
    assert results[2].pnl == 10.0


def test_calculate_profit_range() -> None:
    legs = long_call_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=2.0,
        middle_premium=1.0,
        upper_premium=2.0,
    )

    profit_range = calculate_profit_range(
        legs,
        [
            80.0,
            90.0,
            95.0,
            100.0,
            105.0,
            110.0,
            120.0,
        ],
    )

    assert profit_range == (
        95.0,
        105.0,
    )


def test_calculate_profit_range_returns_none() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=10.0,
        put_premium=10.0,
    )

    profit_range = calculate_profit_range(
        legs,
        [
            90.0,
            100.0,
            110.0,
        ],
    )

    assert profit_range is None


def test_best_case_scenario() -> None:
    legs = long_put_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=6.0,
        middle_premium=10.0,
        upper_premium=15.0,
    )

    result = calculate_best_case_scenario(
        legs,
        [
            80.0,
            90.0,
            100.0,
            110.0,
            120.0,
        ],
    )

    assert result.underlying_price == 100.0
    assert result.pnl == 9.0
    assert result.status == "PROFIT"


def test_worst_case_scenario() -> None:
    legs = long_put_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=6.0,
        middle_premium=10.0,
        upper_premium=15.0,
    )

    result = calculate_worst_case_scenario(
        legs,
        [
            80.0,
            90.0,
            100.0,
            110.0,
            120.0,
        ],
    )

    assert result.pnl == -1.0
    assert result.status == "LOSS"


def test_calculate_risk_analysis() -> None:
    legs = long_put_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=6.0,
        middle_premium=10.0,
        upper_premium=15.0,
    )

    analysis = calculate_risk_analysis(
        legs=legs,
        current_price=100.0,
        scenario_prices=[
            80.0,
            90.0,
            100.0,
            110.0,
            120.0,
        ],
    )

    assert isinstance(
        analysis,
        RiskAnalysis,
    )

    assert analysis.current_price == 100.0
    assert analysis.current_pnl == 9.0

    assert analysis.breakeven_prices == [
        91.0,
        109.0,
    ]

    assert analysis.max_profit == 9.0
    assert analysis.max_loss == -1.0

    assert analysis.profit_probability_range == (
        100.0,
        100.0,
    )

    assert len(analysis.scenarios) == 5


def test_scenario_requires_legs() -> None:
    with pytest.raises(
        ValueError,
        match="At least one option leg",
    ):
        calculate_scenario(
            [],
            100.0,
        )


def test_scenario_rejects_negative_price() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        calculate_scenario(
            legs,
            -1.0,
        )


def test_scenarios_require_prices() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    with pytest.raises(
        ValueError,
        match="At least one underlying price",
    ):
        calculate_scenarios(
            legs,
            [],
        )


def test_risk_analysis_requires_scenarios() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=5.0,
        put_premium=5.0,
    )

    with pytest.raises(
        ValueError,
        match="At least one scenario price",
    ):
        calculate_risk_analysis(
            legs=legs,
            current_price=100.0,
            scenario_prices=[],
        )