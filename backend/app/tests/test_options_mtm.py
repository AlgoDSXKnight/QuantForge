from datetime import date

import pytest

from app.pricing.option_contract import OptionContract
from app.pricing.options_mtm import (
    MTMBar,
    MTMSnapshot,
    calculate_mtm_curve,
    calculate_mtm_snapshot,
)
from app.pricing.strategy_valuation import (
    ContractPosition,
)


def create_call_position() -> ContractPosition:
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


def test_calculate_mtm_snapshot() -> None:
    position = create_call_position()

    bar = MTMBar(
        timestamp=date(2026, 6, 30),
        underlying_price=110.0,
    )

    snapshot = calculate_mtm_snapshot(
        positions=[position],
        bar=bar,
    )

    assert isinstance(
        snapshot,
        MTMSnapshot,
    )

    assert snapshot.timestamp == date(
        2026,
        6,
        30,
    )

    assert snapshot.underlying_price == 110.0

    assert snapshot.market_value > 0.0

    assert snapshot.pnl != 0.0


def test_calculate_mtm_curve() -> None:
    position = create_call_position()

    bars = [
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
    ]

    curve = calculate_mtm_curve(
        positions=[position],
        bars=bars,
    )

    assert len(curve) == 3

    assert curve[0].timestamp == date(
        2026,
        6,
        1,
    )

    assert curve[1].timestamp == date(
        2026,
        6,
        2,
    )

    assert curve[2].timestamp == date(
        2026,
        6,
        3,
    )


def test_mtm_value_changes_with_underlying() -> None:
    position = create_call_position()

    bars = [
        MTMBar(
            timestamp=date(2026, 6, 1),
            underlying_price=90.0,
        ),
        MTMBar(
            timestamp=date(2026, 6, 2),
            underlying_price=110.0,
        ),
    ]

    curve = calculate_mtm_curve(
        positions=[position],
        bars=bars,
    )

    assert (
        curve[1].market_value
        > curve[0].market_value
    )


def test_mtm_value_changes_with_time() -> None:
    position = create_call_position()

    bars = [
        MTMBar(
            timestamp=date(2026, 6, 1),
            underlying_price=100.0,
        ),
        MTMBar(
            timestamp=date(2026, 12, 30),
            underlying_price=100.0,
        ),
    ]

    curve = calculate_mtm_curve(
        positions=[position],
        bars=bars,
    )

    assert (
        curve[0].market_value
        != curve[1].market_value
    )


def test_mtm_requires_positions() -> None:
    bar = MTMBar(
        timestamp=date(2026, 6, 1),
        underlying_price=100.0,
    )

    with pytest.raises(
        ValueError,
        match="At least one position",
    ):
        calculate_mtm_snapshot(
            positions=[],
            bar=bar,
        )


def test_mtm_curve_requires_positions() -> None:
    bars = [
        MTMBar(
            timestamp=date(2026, 6, 1),
            underlying_price=100.0,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="At least one position",
    ):
        calculate_mtm_curve(
            positions=[],
            bars=bars,
        )


def test_mtm_curve_requires_bars() -> None:
    position = create_call_position()

    with pytest.raises(
        ValueError,
        match="At least one MTM bar",
    ):
        calculate_mtm_curve(
            positions=[position],
            bars=[],
        )


def test_mtm_rejects_non_positive_price() -> None:
    position = create_call_position()

    bar = MTMBar(
        timestamp=date(2026, 6, 1),
        underlying_price=0.0,
    )

    with pytest.raises(
        ValueError,
        match="Underlying price",
    ):
        calculate_mtm_snapshot(
            positions=[position],
            bar=bar,
        )


def test_mtm_rejects_non_chronological_bars() -> None:
    position = create_call_position()

    bars = [
        MTMBar(
            timestamp=date(2026, 6, 2),
            underlying_price=100.0,
        ),
        MTMBar(
            timestamp=date(2026, 6, 1),
            underlying_price=105.0,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="strictly chronological",
    ):
        calculate_mtm_curve(
            positions=[position],
            bars=bars,
        )

def test_mtm_value_changes_with_volatility() -> None:
    position = create_call_position()

    bars = [
        MTMBar(
            timestamp=date(2026, 6, 1),
            underlying_price=100.0,
            volatility=0.20,
        ),
        MTMBar(
            timestamp=date(2026, 6, 2),
            underlying_price=100.0,
            volatility=0.40,
        ),
    ]

    curve = calculate_mtm_curve(
        positions=[position],
        bars=bars,
    )

    assert (
        curve[1].market_value
        > curve[0].market_value
    )

    assert curve[0].volatility == 0.20
    assert curve[1].volatility == 0.40