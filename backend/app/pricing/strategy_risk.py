from dataclasses import dataclass

from app.pricing.options_strategy import (
    OptionLeg,
    calculate_breakeven_prices,
    calculate_max_loss,
    calculate_max_profit,
    calculate_strategy_pnl,
)


@dataclass(frozen=True)
class ScenarioResult:
    underlying_price: float
    pnl: float
    status: str


@dataclass(frozen=True)
class RiskAnalysis:
    current_price: float
    current_pnl: float
    breakeven_prices: list[float]
    max_profit: float | None
    max_loss: float | None
    profit_probability_range: tuple[float, float] | None
    scenarios: list[ScenarioResult]


def _validate_inputs(
    legs: list[OptionLeg],
    underlying_price: float,
) -> None:
    if not legs:
        raise ValueError(
            "At least one option leg is required."
        )

    if underlying_price < 0:
        raise ValueError(
            "Underlying price cannot be negative."
        )


def calculate_scenario(
    legs: list[OptionLeg],
    underlying_price: float,
) -> ScenarioResult:
    """
    Calculate strategy P&L at one underlying price.
    """

    _validate_inputs(
        legs,
        underlying_price,
    )

    pnl = calculate_strategy_pnl(
        legs,
        underlying_price,
    )

    if pnl > 1e-9:
        status = "PROFIT"
    elif pnl < -1e-9:
        status = "LOSS"
    else:
        status = "BREAKEVEN"

    return ScenarioResult(
        underlying_price=underlying_price,
        pnl=pnl,
        status=status,
    )


def calculate_scenarios(
    legs: list[OptionLeg],
    underlying_prices: list[float],
) -> list[ScenarioResult]:
    """
    Calculate strategy P&L across multiple underlying prices.
    """

    if not legs:
        raise ValueError(
            "At least one option leg is required."
        )

    if not underlying_prices:
        raise ValueError(
            "At least one underlying price is required."
        )

    return [
        calculate_scenario(
            legs,
            price,
        )
        for price in underlying_prices
    ]


def calculate_profit_range(
    legs: list[OptionLeg],
    underlying_prices: list[float],
) -> tuple[float, float] | None:
    """
    Return the lowest and highest underlying prices
    in the supplied range that produce a profit.

    Returns None if none of the supplied prices are profitable.
    """

    scenarios = calculate_scenarios(
        legs,
        underlying_prices,
    )

    profitable_prices = [
        scenario.underlying_price
        for scenario in scenarios
        if scenario.pnl > 1e-9
    ]

    if not profitable_prices:
        return None

    return (
        min(profitable_prices),
        max(profitable_prices),
    )


def calculate_worst_case_scenario(
    legs: list[OptionLeg],
    underlying_prices: list[float],
) -> ScenarioResult:
    """
    Return the scenario with the lowest P&L.
    """

    scenarios = calculate_scenarios(
        legs,
        underlying_prices,
    )

    return min(
        scenarios,
        key=lambda scenario: scenario.pnl,
    )


def calculate_best_case_scenario(
    legs: list[OptionLeg],
    underlying_prices: list[float],
) -> ScenarioResult:
    """
    Return the scenario with the highest P&L.
    """

    scenarios = calculate_scenarios(
        legs,
        underlying_prices,
    )

    return max(
        scenarios,
        key=lambda scenario: scenario.pnl,
    )


def calculate_risk_analysis(
    legs: list[OptionLeg],
    current_price: float,
    scenario_prices: list[float],
) -> RiskAnalysis:
    """
    Run the complete strategy risk/scenario analysis.
    """

    _validate_inputs(
        legs,
        current_price,
    )

    if not scenario_prices:
        raise ValueError(
            "At least one scenario price is required."
        )

    scenarios = calculate_scenarios(
        legs,
        scenario_prices,
    )

    return RiskAnalysis(
        current_price=current_price,
        current_pnl=calculate_strategy_pnl(
            legs,
            current_price,
        ),
        breakeven_prices=calculate_breakeven_prices(
            legs,
        ),
        max_profit=calculate_max_profit(
            legs,
        ),
        max_loss=calculate_max_loss(
            legs,
        ),
        profit_probability_range=calculate_profit_range(
            legs,
            scenario_prices,
        ),
        scenarios=scenarios,
    )