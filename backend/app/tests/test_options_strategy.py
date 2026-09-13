import pytest

from app.pricing.options_strategy import (
    OptionLeg,
    StrategyPayoff,
    bear_call_spread,
    bear_put_spread,
    bull_call_spread,
    bull_put_spread,
    calculate_breakeven_prices,
    calculate_leg_payoff,
    calculate_leg_pnl,
    calculate_max_loss,
    calculate_max_profit,
    calculate_net_premium,
    calculate_strategy_analytics,
    calculate_strategy_payoff,
    calculate_strategy_payoff_curve,
    calculate_strategy_pnl,
    long_call_butterfly,
    long_iron_butterfly,
    long_iron_condor,
    long_straddle,
    long_strangle,
    short_call_butterfly,
    short_iron_butterfly,
    short_iron_condor,
    short_straddle,
    short_strangle,
    long_put_butterfly,
    short_put_butterfly,
)


# ============================================================================
# Option Leg
# ============================================================================


def test_long_call_payoff_in_the_money() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
    )

    assert calculate_leg_payoff(
        leg,
        120.0,
    ) == 20.0


def test_long_call_payoff_out_of_the_money() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
    )

    assert calculate_leg_payoff(
        leg,
        80.0,
    ) == 0.0


def test_long_put_payoff_in_the_money() -> None:
    leg = OptionLeg(
        option_type="PUT",
        position="LONG",
        strike_price=100.0,
        premium=8.0,
    )

    assert calculate_leg_payoff(
        leg,
        80.0,
    ) == 20.0


def test_long_put_payoff_out_of_the_money() -> None:
    leg = OptionLeg(
        option_type="PUT",
        position="LONG",
        strike_price=100.0,
        premium=8.0,
    )

    assert calculate_leg_payoff(
        leg,
        120.0,
    ) == 0.0


def test_short_call_payoff() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="SHORT",
        strike_price=100.0,
        premium=10.0,
    )

    assert calculate_leg_payoff(
        leg,
        120.0,
    ) == -20.0


def test_short_put_payoff() -> None:
    leg = OptionLeg(
        option_type="PUT",
        position="SHORT",
        strike_price=100.0,
        premium=8.0,
    )

    assert calculate_leg_payoff(
        leg,
        80.0,
    ) == -20.0


# ============================================================================
# Individual Leg P&L
# ============================================================================


def test_long_call_pnl() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
    )

    assert calculate_leg_pnl(
        leg,
        120.0,
    ) == 10.0


def test_long_call_loss_when_out_of_the_money() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
    )

    assert calculate_leg_pnl(
        leg,
        80.0,
    ) == -10.0


def test_short_call_pnl() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="SHORT",
        strike_price=100.0,
        premium=10.0,
    )

    assert calculate_leg_pnl(
        leg,
        120.0,
    ) == -10.0


def test_short_call_profit_when_out_of_the_money() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="SHORT",
        strike_price=100.0,
        premium=10.0,
    )

    assert calculate_leg_pnl(
        leg,
        80.0,
    ) == 10.0


def test_quantity_scales_payoff() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
        quantity=5,
    )

    assert calculate_leg_payoff(
        leg,
        120.0,
    ) == 100.0


def test_quantity_scales_pnl() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
        quantity=5,
    )

    assert calculate_leg_pnl(
        leg,
        120.0,
    ) == 50.0


# ============================================================================
# Strategy Payoff / P&L
# ============================================================================


def test_bull_call_strategy_payoff() -> None:
    legs = [
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=100.0,
            premium=10.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=120.0,
            premium=4.0,
        ),
    ]

    assert calculate_strategy_payoff(
        legs,
        130.0,
    ) == 20.0


def test_bull_call_strategy_pnl() -> None:
    legs = [
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=100.0,
            premium=10.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=120.0,
            premium=4.0,
        ),
    ]

    assert calculate_strategy_pnl(
        legs,
        130.0,
    ) == 14.0


def test_bull_call_strategy_pnl_at_breakeven() -> None:
    legs = [
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=100.0,
            premium=10.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=120.0,
            premium=4.0,
        ),
    ]

    assert calculate_strategy_pnl(
        legs,
        106.0,
    ) == pytest.approx(0.0)


def test_bear_put_strategy() -> None:
    legs = [
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=120.0,
            premium=10.0,
        ),
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=100.0,
            premium=4.0,
        ),
    ]

    assert calculate_strategy_pnl(
        legs,
        90.0,
    ) == 14.0


def test_payoff_curve() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
    )

    results = calculate_strategy_payoff_curve(
        legs=[leg],
        underlying_prices=[
            80.0,
            100.0,
            120.0,
        ],
    )

    assert len(results) == 3

    assert results[0] == StrategyPayoff(
        underlying_price=80.0,
        payoff=0.0,
        pnl=-10.0,
    )

    assert results[1] == StrategyPayoff(
        underlying_price=100.0,
        payoff=0.0,
        pnl=-10.0,
    )

    assert results[2] == StrategyPayoff(
        underlying_price=120.0,
        payoff=20.0,
        pnl=10.0,
    )


# ============================================================================
# Validation
# ============================================================================


@pytest.mark.parametrize(
    "option_type",
    ["STOCK", "", "OPTION"],
)
def test_invalid_option_type(
    option_type: str,
) -> None:
    leg = OptionLeg(
        option_type=option_type,
        position="LONG",
        strike_price=100.0,
        premium=10.0,
    )

    with pytest.raises(ValueError):
        calculate_leg_payoff(
            leg,
            100.0,
        )


@pytest.mark.parametrize(
    "position",
    ["BUY", "SELL", "", "HOLD"],
)
def test_invalid_position(
    position: str,
) -> None:
    leg = OptionLeg(
        option_type="CALL",
        position=position,
        strike_price=100.0,
        premium=10.0,
    )

    with pytest.raises(ValueError):
        calculate_leg_payoff(
            leg,
            100.0,
        )


@pytest.mark.parametrize(
    "strike_price",
    [0.0, -1.0],
)
def test_invalid_strike_price(
    strike_price: float,
) -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="LONG",
        strike_price=strike_price,
        premium=10.0,
    )

    with pytest.raises(ValueError):
        calculate_leg_payoff(
            leg,
            100.0,
        )


def test_negative_premium_rejected() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="LONG",
        strike_price=100.0,
        premium=-1.0,
    )

    with pytest.raises(ValueError):
        calculate_leg_payoff(
            leg,
            100.0,
        )


@pytest.mark.parametrize(
    "quantity",
    [0, -1],
)
def test_invalid_quantity(
    quantity: int,
) -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
        quantity=quantity,
    )

    with pytest.raises(ValueError):
        calculate_leg_payoff(
            leg,
            100.0,
        )


def test_non_integer_quantity_rejected() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
        quantity=1.5,
    )

    with pytest.raises(ValueError):
        calculate_leg_payoff(
            leg,
            100.0,
        )


def test_negative_underlying_price_rejected() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
    )

    with pytest.raises(ValueError):
        calculate_leg_payoff(
            leg,
            -1.0,
        )


def test_empty_strategy_rejected() -> None:
    with pytest.raises(ValueError):
        calculate_strategy_payoff(
            legs=[],
            underlying_price=100.0,
        )


def test_empty_strategy_pnl_rejected() -> None:
    with pytest.raises(ValueError):
        calculate_strategy_pnl(
            legs=[],
            underlying_price=100.0,
        )


def test_empty_payoff_curve_rejected() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
    )

    with pytest.raises(ValueError):
        calculate_strategy_payoff_curve(
            legs=[leg],
            underlying_prices=[],
        )


# ============================================================================
# Net Premium
# ============================================================================


def test_net_premium_for_bull_call_spread() -> None:
    legs = [
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=100.0,
            premium=10.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=120.0,
            premium=4.0,
        ),
    ]

    assert calculate_net_premium(legs) == 6.0


def test_net_premium_for_credit_spread() -> None:
    legs = [
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=100.0,
            premium=10.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=120.0,
            premium=4.0,
        ),
    ]

    assert calculate_net_premium(legs) == -6.0


# ============================================================================
# Basic Analytics
# ============================================================================


def test_bull_call_spread_breakeven() -> None:
    legs = [
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=100.0,
            premium=10.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=120.0,
            premium=4.0,
        ),
    ]

    assert calculate_breakeven_prices(
        legs
    ) == [106.0]


def test_bull_call_spread_max_profit() -> None:
    legs = [
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=100.0,
            premium=10.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=120.0,
            premium=4.0,
        ),
    ]

    assert calculate_max_profit(legs) == 14.0


def test_bull_call_spread_max_loss() -> None:
    legs = [
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=100.0,
            premium=10.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=120.0,
            premium=4.0,
        ),
    ]

    assert calculate_max_loss(legs) == -6.0


def test_bear_put_spread_analytics() -> None:
    legs = [
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=120.0,
            premium=10.0,
        ),
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=100.0,
            premium=4.0,
        ),
    ]

    analytics = calculate_strategy_analytics(
        legs
    )

    assert analytics.net_premium == 6.0
    assert analytics.breakeven_prices == [114.0]
    assert analytics.max_profit == 14.0
    assert analytics.max_loss == -6.0


def test_long_call_has_unlimited_profit() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
    )

    assert calculate_max_profit([leg]) is None


def test_short_call_has_unlimited_loss() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="SHORT",
        strike_price=100.0,
        premium=10.0,
    )

    assert calculate_max_loss([leg]) is None


def test_long_call_max_loss_is_premium() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
    )

    assert calculate_max_loss([leg]) == -10.0


def test_short_call_max_profit_is_premium() -> None:
    leg = OptionLeg(
        option_type="CALL",
        position="SHORT",
        strike_price=100.0,
        premium=10.0,
    )

    assert calculate_max_profit([leg]) == 10.0


def test_long_put_max_profit() -> None:
    leg = OptionLeg(
        option_type="PUT",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
    )

    assert calculate_max_profit([leg]) == 90.0


def test_long_put_max_loss_is_premium() -> None:
    leg = OptionLeg(
        option_type="PUT",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
    )

    assert calculate_max_loss([leg]) == -10.0


def test_long_put_breakeven() -> None:
    leg = OptionLeg(
        option_type="PUT",
        position="LONG",
        strike_price=100.0,
        premium=10.0,
    )

    assert calculate_breakeven_prices(
        [leg]
    ) == [90.0]


# ============================================================================
# Spread Constructors
# ============================================================================


def test_bull_call_spread_constructor() -> None:
    legs = bull_call_spread(
        lower_strike=100.0,
        upper_strike=120.0,
        long_premium=10.0,
        short_premium=4.0,
    )

    assert legs == [
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=100.0,
            premium=10.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=120.0,
            premium=4.0,
        ),
    ]


def test_bear_call_spread_constructor() -> None:
    legs = bear_call_spread(
        lower_strike=100.0,
        upper_strike=120.0,
        short_premium=10.0,
        long_premium=4.0,
    )

    assert legs == [
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=100.0,
            premium=10.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=120.0,
            premium=4.0,
        ),
    ]


def test_bull_put_spread_constructor() -> None:
    legs = bull_put_spread(
        lower_strike=100.0,
        upper_strike=120.0,
        long_premium=4.0,
        short_premium=10.0,
    )

    assert legs == [
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=120.0,
            premium=10.0,
        ),
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=100.0,
            premium=4.0,
        ),
    ]


def test_bear_put_spread_constructor() -> None:
    legs = bear_put_spread(
        lower_strike=100.0,
        upper_strike=120.0,
        long_premium=10.0,
        short_premium=4.0,
    )

    assert legs == [
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=120.0,
            premium=10.0,
        ),
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=100.0,
            premium=4.0,
        ),
    ]


def test_bull_put_spread_analytics() -> None:
    legs = bull_put_spread(
        lower_strike=100.0,
        upper_strike=120.0,
        long_premium=4.0,
        short_premium=10.0,
    )

    analytics = calculate_strategy_analytics(
        legs
    )

    assert analytics.net_premium == -6.0
    assert analytics.breakeven_prices == [114.0]
    assert analytics.max_profit == 6.0
    assert analytics.max_loss == -14.0


def test_bear_call_spread_analytics() -> None:
    legs = bear_call_spread(
        lower_strike=100.0,
        upper_strike=120.0,
        short_premium=10.0,
        long_premium=4.0,
    )

    analytics = calculate_strategy_analytics(
        legs
    )

    assert analytics.net_premium == -6.0
    assert analytics.breakeven_prices == [106.0]
    assert analytics.max_profit == 6.0
    assert analytics.max_loss == -14.0


def test_strategy_constructor_quantity() -> None:
    legs = bull_call_spread(
        lower_strike=100.0,
        upper_strike=120.0,
        long_premium=10.0,
        short_premium=4.0,
        quantity=5,
    )

    assert all(
        leg.quantity == 5
        for leg in legs
    )


# ============================================================================
# Straddle / Strangle
# ============================================================================


def test_long_straddle_constructor() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=6.0,
        put_premium=5.0,
    )

    assert legs == [
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=100.0,
            premium=6.0,
        ),
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=100.0,
            premium=5.0,
        ),
    ]


def test_short_straddle_constructor() -> None:
    legs = short_straddle(
        strike_price=100.0,
        call_premium=6.0,
        put_premium=5.0,
    )

    assert legs == [
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=100.0,
            premium=6.0,
        ),
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=100.0,
            premium=5.0,
        ),
    ]


def test_long_strangle_constructor() -> None:
    legs = long_strangle(
        put_strike=90.0,
        call_strike=110.0,
        put_premium=4.0,
        call_premium=5.0,
    )

    assert legs == [
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=90.0,
            premium=4.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=110.0,
            premium=5.0,
        ),
    ]


def test_short_strangle_constructor() -> None:
    legs = short_strangle(
        put_strike=90.0,
        call_strike=110.0,
        put_premium=4.0,
        call_premium=5.0,
    )

    assert legs == [
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=90.0,
            premium=4.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=110.0,
            premium=5.0,
        ),
    ]


def test_long_straddle_analytics() -> None:
    legs = long_straddle(
        strike_price=100.0,
        call_premium=6.0,
        put_premium=5.0,
    )

    analytics = calculate_strategy_analytics(
        legs
    )

    assert analytics.net_premium == 11.0
    assert analytics.breakeven_prices == [89.0, 111.0]
    assert analytics.max_profit is None
    assert analytics.max_loss == -11.0


def test_short_straddle_analytics() -> None:
    legs = short_straddle(
        strike_price=100.0,
        call_premium=6.0,
        put_premium=5.0,
    )

    analytics = calculate_strategy_analytics(
        legs
    )

    assert analytics.net_premium == -11.0
    assert analytics.breakeven_prices == [89.0, 111.0]
    assert analytics.max_profit == 11.0
    assert analytics.max_loss is None


def test_long_strangle_analytics() -> None:
    legs = long_strangle(
        put_strike=90.0,
        call_strike=110.0,
        put_premium=4.0,
        call_premium=5.0,
    )

    analytics = calculate_strategy_analytics(
        legs
    )

    assert analytics.net_premium == 9.0
    assert analytics.breakeven_prices == [81.0, 119.0]
    assert analytics.max_profit is None
    assert analytics.max_loss == -9.0


def test_short_strangle_analytics() -> None:
    legs = short_strangle(
        put_strike=90.0,
        call_strike=110.0,
        put_premium=4.0,
        call_premium=5.0,
    )

    analytics = calculate_strategy_analytics(
        legs
    )

    assert analytics.net_premium == -9.0
    assert analytics.breakeven_prices == [81.0, 119.0]
    assert analytics.max_profit == 9.0
    assert analytics.max_loss is None


def test_long_strangle_breakevens() -> None:
    legs = long_strangle(
        put_strike=90.0,
        call_strike=110.0,
        put_premium=3.0,
        call_premium=4.0,
    )

    assert calculate_breakeven_prices(
        legs
    ) == [83.0, 117.0]


# ============================================================================
# Butterflies
# ============================================================================


def test_long_call_butterfly_constructor() -> None:
    legs = long_call_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=15.0,
        middle_premium=10.0,
        upper_premium=6.0,
    )

    assert legs == [
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=90.0,
            premium=15.0,
            quantity=1,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=100.0,
            premium=10.0,
            quantity=2,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=110.0,
            premium=6.0,
            quantity=1,
        ),
    ]


def test_short_call_butterfly_constructor() -> None:
    legs = short_call_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=15.0,
        middle_premium=10.0,
        upper_premium=6.0,
    )

    assert legs == [
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=90.0,
            premium=15.0,
            quantity=1,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=100.0,
            premium=10.0,
            quantity=2,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=110.0,
            premium=6.0,
            quantity=1,
        ),
    ]


def test_long_call_butterfly_analytics() -> None:
    legs = long_call_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=15.0,
        middle_premium=10.0,
        upper_premium=6.0,
    )

    analytics = calculate_strategy_analytics(
        legs
    )

    assert analytics.net_premium == 1.0
    assert analytics.breakeven_prices == [91.0, 109.0]
    assert analytics.max_profit == 9.0
    assert analytics.max_loss == -1.0


def test_short_call_butterfly_analytics() -> None:
    legs = short_call_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=15.0,
        middle_premium=10.0,
        upper_premium=6.0,
    )

    analytics = calculate_strategy_analytics(
        legs
    )

    assert analytics.net_premium == -1.0
    assert analytics.breakeven_prices == [91.0, 109.0]
    assert analytics.max_profit == 1.0
    assert analytics.max_loss == -9.0


def test_long_call_butterfly_requires_equal_strike_spacing() -> None:
    with pytest.raises(
        ValueError,
        match="equally spaced",
    ):
        long_call_butterfly(
            lower_strike=90.0,
            middle_strike=100.0,
            upper_strike=115.0,
            lower_premium=15.0,
            middle_premium=10.0,
            upper_premium=5.0,
        )


def test_short_call_butterfly_requires_equal_strike_spacing() -> None:
    with pytest.raises(
        ValueError,
        match="equally spaced",
    ):
        short_call_butterfly(
            lower_strike=90.0,
            middle_strike=100.0,
            upper_strike=115.0,
            lower_premium=15.0,
            middle_premium=10.0,
            upper_premium=5.0,
        )


# ============================================================================
# Iron Condors
# ============================================================================


def test_long_iron_condor_constructor() -> None:
    legs = long_iron_condor(
        put_long_strike=90.0,
        put_short_strike=100.0,
        call_short_strike=110.0,
        call_long_strike=120.0,
        put_long_premium=2.0,
        put_short_premium=5.0,
        call_short_premium=5.0,
        call_long_premium=2.0,
    )

    assert legs == [
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=90.0,
            premium=2.0,
        ),
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=100.0,
            premium=5.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=110.0,
            premium=5.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=120.0,
            premium=2.0,
        ),
    ]


def test_short_iron_condor_constructor() -> None:
    legs = short_iron_condor(
        put_long_strike=90.0,
        put_short_strike=100.0,
        call_short_strike=110.0,
        call_long_strike=120.0,
        put_long_premium=2.0,
        put_short_premium=5.0,
        call_short_premium=5.0,
        call_long_premium=2.0,
    )

    assert legs == [
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=90.0,
            premium=2.0,
        ),
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=100.0,
            premium=5.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=110.0,
            premium=5.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=120.0,
            premium=2.0,
        ),
    ]


def test_long_iron_condor_analytics() -> None:
    legs = long_iron_condor(
        put_long_strike=90.0,
        put_short_strike=100.0,
        call_short_strike=110.0,
        call_long_strike=120.0,
        put_long_premium=2.0,
        put_short_premium=5.0,
        call_short_premium=5.0,
        call_long_premium=2.0,
    )

    analytics = calculate_strategy_analytics(
        legs
    )

    assert analytics.net_premium == -6.0
    assert analytics.breakeven_prices == [94.0, 116.0]
    assert analytics.max_profit == 6.0
    assert analytics.max_loss == -4.0


def test_short_iron_condor_analytics() -> None:
    legs = short_iron_condor(
        put_long_strike=90.0,
        put_short_strike=100.0,
        call_short_strike=110.0,
        call_long_strike=120.0,
        put_long_premium=2.0,
        put_short_premium=5.0,
        call_short_premium=5.0,
        call_long_premium=2.0,
    )

    analytics = calculate_strategy_analytics(
        legs
    )

    assert analytics.net_premium == 6.0
    assert analytics.breakeven_prices == [94.0, 116.0]
    assert analytics.max_profit == 4.0
    assert analytics.max_loss == -6.0


def test_iron_condor_quantity() -> None:
    legs = short_iron_condor(
        put_long_strike=90.0,
        put_short_strike=100.0,
        call_short_strike=110.0,
        call_long_strike=120.0,
        put_long_premium=2.0,
        put_short_premium=5.0,
        call_short_premium=5.0,
        call_long_premium=2.0,
        quantity=5,
    )

    assert all(
        leg.quantity == 5
        for leg in legs
    )


def test_iron_condor_requires_correct_strike_order() -> None:
    with pytest.raises(
        ValueError,
        match="put_long < put_short < call_short < call_long",
    ):
        long_iron_condor(
            put_long_strike=100.0,
            put_short_strike=90.0,
            call_short_strike=110.0,
            call_long_strike=120.0,
            put_long_premium=2.0,
            put_short_premium=5.0,
            call_short_premium=5.0,
            call_long_premium=2.0,
        )


def test_iron_condor_rejects_non_positive_strike() -> None:
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        short_iron_condor(
            put_long_strike=0.0,
            put_short_strike=100.0,
            call_short_strike=110.0,
            call_long_strike=120.0,
            put_long_premium=2.0,
            put_short_premium=5.0,
            call_short_premium=5.0,
            call_long_premium=2.0,
        )


# ============================================================================
# Iron Butterflies
# ============================================================================


def test_long_iron_butterfly_constructor() -> None:
    legs = long_iron_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_put_premium=2.0,
        middle_put_premium=6.0,
        middle_call_premium=5.0,
        upper_call_premium=2.0,
    )

    assert legs == [
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=90.0,
            premium=2.0,
        ),
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=100.0,
            premium=6.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=100.0,
            premium=5.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=110.0,
            premium=2.0,
        ),
    ]


def test_short_iron_butterfly_constructor() -> None:
    legs = short_iron_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_put_premium=2.0,
        middle_put_premium=6.0,
        middle_call_premium=5.0,
        upper_call_premium=2.0,
    )

    assert legs == [
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=90.0,
            premium=2.0,
        ),
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=100.0,
            premium=6.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="LONG",
            strike_price=100.0,
            premium=5.0,
        ),
        OptionLeg(
            option_type="CALL",
            position="SHORT",
            strike_price=110.0,
            premium=2.0,
        ),
    ]


def test_long_iron_butterfly_analytics() -> None:
    legs = long_iron_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_put_premium=2.0,
        middle_put_premium=6.0,
        middle_call_premium=5.0,
        upper_call_premium=2.0,
    )

    analytics = calculate_strategy_analytics(
        legs
    )

    assert analytics.net_premium == -7.0
    assert analytics.breakeven_prices == [93.0, 107.0]
    assert analytics.max_profit == 7.0
    assert analytics.max_loss == -3.0


def test_short_iron_butterfly_analytics() -> None:
    legs = short_iron_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_put_premium=2.0,
        middle_put_premium=6.0,
        middle_call_premium=5.0,
        upper_call_premium=2.0,
    )

    analytics = calculate_strategy_analytics(
        legs
    )

    assert analytics.net_premium == 7.0
    assert analytics.breakeven_prices == [93.0, 107.0]
    assert analytics.max_profit == 3.0
    assert analytics.max_loss == -7.0


def test_iron_butterfly_quantity() -> None:
    legs = long_iron_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_put_premium=2.0,
        middle_put_premium=6.0,
        middle_call_premium=5.0,
        upper_call_premium=2.0,
        quantity=5,
    )

    assert all(
        leg.quantity == 5
        for leg in legs
    )


def test_iron_butterfly_does_not_require_equal_spacing() -> None:
    legs = long_iron_butterfly(
        lower_strike=85.0,
        middle_strike=100.0,
        upper_strike=120.0,
        lower_put_premium=2.0,
        middle_put_premium=6.0,
        middle_call_premium=5.0,
        upper_call_premium=2.0,
    )

    assert legs[0].strike_price == 85.0
    assert legs[1].strike_price == 100.0
    assert legs[2].strike_price == 100.0
    assert legs[3].strike_price == 120.0


def test_iron_butterfly_requires_correct_strike_order() -> None:
    with pytest.raises(
        ValueError,
        match="lower < middle < upper",
    ):
        long_iron_butterfly(
            lower_strike=100.0,
            middle_strike=90.0,
            upper_strike=110.0,
            lower_put_premium=2.0,
            middle_put_premium=6.0,
            middle_call_premium=5.0,
            upper_call_premium=2.0,
        )


def test_iron_butterfly_rejects_non_positive_strike() -> None:
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        short_iron_butterfly(
            lower_strike=0.0,
            middle_strike=100.0,
            upper_strike=110.0,
            lower_put_premium=2.0,
            middle_put_premium=6.0,
            middle_call_premium=5.0,
            upper_call_premium=2.0,
        )


# ============================================================================
# Bear Put Spread Corrected Analytics
# ============================================================================


def test_bear_put_spread_max_profit_and_loss() -> None:
    legs = bear_put_spread(
        lower_strike=90.0,
        upper_strike=100.0,
        long_premium=6.0,
        short_premium=2.0,
    )

    assert calculate_max_profit(
        legs
    ) == 6.0

    assert calculate_max_loss(
        legs
    ) == -4.0

# ============================================================================
# Put Butterflies
# ============================================================================


def test_long_put_butterfly_constructor() -> None:
    legs = long_put_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=2.0,
        middle_premium=10.0,
        upper_premium=15.0,
    )

    assert legs == [
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=90.0,
            premium=2.0,
            quantity=1,
        ),
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=100.0,
            premium=10.0,
            quantity=2,
        ),
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=110.0,
            premium=15.0,
            quantity=1,
        ),
    ]


def test_short_put_butterfly_constructor() -> None:
    legs = short_put_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=2.0,
        middle_premium=10.0,
        upper_premium=15.0,
    )

    assert legs == [
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=90.0,
            premium=2.0,
            quantity=1,
        ),
        OptionLeg(
            option_type="PUT",
            position="LONG",
            strike_price=100.0,
            premium=10.0,
            quantity=2,
        ),
        OptionLeg(
            option_type="PUT",
            position="SHORT",
            strike_price=110.0,
            premium=15.0,
            quantity=1,
        ),
    ]


def test_long_put_butterfly_analytics() -> None:
    legs = long_put_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=6.0,
        middle_premium=10.0,
        upper_premium=15.0,
    )

    analytics = calculate_strategy_analytics(
        legs
    )

    assert analytics.net_premium == 1.0
    assert analytics.breakeven_prices == [91.0, 109.0]
    assert analytics.max_profit == 9.0
    assert analytics.max_loss == -1.0


def test_short_put_butterfly_analytics() -> None:
    legs = short_put_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=6.0,
        middle_premium=10.0,
        upper_premium=15.0,
    )

    analytics = calculate_strategy_analytics(
        legs
    )

    assert analytics.net_premium == -1.0
    assert analytics.breakeven_prices == [91.0, 109.0]
    assert analytics.max_profit == 1.0
    assert analytics.max_loss == -9.0


def test_put_butterfly_quantity() -> None:
    legs = long_put_butterfly(
        lower_strike=90.0,
        middle_strike=100.0,
        upper_strike=110.0,
        lower_premium=2.0,
        middle_premium=10.0,
        upper_premium=15.0,
        quantity=5,
    )

    assert legs[0].quantity == 5
    assert legs[1].quantity == 10
    assert legs[2].quantity == 5


def test_long_put_butterfly_requires_equal_strike_spacing() -> None:
    with pytest.raises(
        ValueError,
        match="equally spaced",
    ):
        long_put_butterfly(
            lower_strike=90.0,
            middle_strike=100.0,
            upper_strike=115.0,
            lower_premium=2.0,
            middle_premium=10.0,
            upper_premium=15.0,
        )


def test_short_put_butterfly_requires_equal_strike_spacing() -> None:
    with pytest.raises(
        ValueError,
        match="equally spaced",
    ):
        short_put_butterfly(
            lower_strike=90.0,
            middle_strike=100.0,
            upper_strike=115.0,
            lower_premium=2.0,
            middle_premium=10.0,
            upper_premium=15.0,
        )


def test_put_butterfly_requires_correct_strike_order() -> None:
    with pytest.raises(
        ValueError,
        match="lower < middle < upper",
    ):
        long_put_butterfly(
            lower_strike=100.0,
            middle_strike=90.0,
            upper_strike=110.0,
            lower_premium=2.0,
            middle_premium=10.0,
            upper_premium=15.0,
        )