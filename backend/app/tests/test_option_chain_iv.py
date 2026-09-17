from datetime import date

import pytest

from app.pricing.option_chain import OptionChain
from app.pricing.option_chain_iv import (
    OptionChainIVResult,
    average_chain_iv,
    calculate_option_chain_iv,
    calculate_option_iv,
    filter_chain_iv_by_expiration,
    filter_chain_iv_by_option_type,
)
from app.pricing.option_market_data import OptionMarketData


def create_option(
    option_type: str,
    strike: float,
    bid: float,
    ask: float,
    expiration: date = date(2026, 12, 31),
) -> OptionMarketData:
    return OptionMarketData(
        underlying="INFY",
        timestamp=date(2026, 9, 1),
        option_type=option_type,
        strike=strike,
        expiration=expiration,
        bid=bid,
        ask=ask,
        last_price=(bid + ask) / 2.0,
        underlying_price=1900.0,
    )


def create_chain() -> OptionChain:
    return OptionChain(
        underlying="INFY",
        timestamp=date(2026, 9, 1),
        underlying_price=1900.0,
        options=[
            create_option(
                "CALL",
                1900.0,
                90.0,
                100.0,
            ),
            create_option(
                "PUT",
                1900.0,
                85.0,
                95.0,
            ),
            create_option(
                "CALL",
                2000.0,
                45.0,
                55.0,
            ),
            create_option(
                "PUT",
                2000.0,
                135.0,
                145.0,
            ),
        ],
    )


def test_calculate_option_iv() -> None:
    option = create_option(
        "CALL",
        1900.0,
        90.0,
        100.0,
    )

    volatility = calculate_option_iv(
        option=option,
        risk_free_rate=0.06,
    )

    assert volatility > 0
    assert volatility < 2.0


def test_calculate_option_iv_uses_mid_price() -> None:
    option = create_option(
        "CALL",
        1900.0,
        90.0,
        100.0,
    )

    volatility = calculate_option_iv(
        option=option,
        risk_free_rate=0.06,
    )

    assert volatility > 0


def test_calculate_option_iv_rejects_invalid_rate() -> None:
    option = create_option(
        "CALL",
        1900.0,
        90.0,
        100.0,
    )

    with pytest.raises(
        ValueError,
        match="Risk-free rate must be greater than or equal to -1",
    ):
        calculate_option_iv(
            option=option,
            risk_free_rate=-1.1,
        )


def test_calculate_option_chain_iv() -> None:
    chain = create_chain()

    result = calculate_option_chain_iv(
        option_chain=chain,
        risk_free_rate=0.06,
    )

    assert isinstance(result, OptionChainIVResult)
    assert len(result.points) == 4
    assert result.failed_contracts == 0

    assert result.points[0].underlying == "INFY"
    assert result.points[0].option_type == "CALL"
    assert result.points[0].strike == 1900.0
    assert result.points[0].option_price == 95.0
    assert result.points[0].underlying_price == 1900.0
    assert result.points[0].implied_volatility > 0


def test_calculate_option_chain_iv_preserves_contract_information() -> None:
    chain = create_chain()

    result = calculate_option_chain_iv(
        option_chain=chain,
        risk_free_rate=0.06,
    )

    expirations = {
        point.expiration
        for point in result.points
    }

    strikes = {
        point.strike
        for point in result.points
    }

    option_types = {
        point.option_type
        for point in result.points
    }

    assert expirations == {date(2026, 12, 31)}
    assert strikes == {1900.0, 2000.0}
    assert option_types == {"CALL", "PUT"}


def test_calculate_option_chain_iv_rejects_invalid_rate() -> None:
    chain = create_chain()

    with pytest.raises(
        ValueError,
        match="Risk-free rate must be greater than or equal to -1",
    ):
        calculate_option_chain_iv(
            option_chain=chain,
            risk_free_rate=-1.1,
        )


def test_calculate_option_chain_iv_tracks_failed_contracts() -> None:
    valid_option = create_option(
        "CALL",
        1900.0,
        90.0,
        100.0,
    )

    invalid_option = create_option(
        "CALL",
        2000.0,
        0.0,
        0.0,
    )

    chain = OptionChain(
        underlying="INFY",
        timestamp=date(2026, 9, 1),
        underlying_price=1900.0,
        options=[
            valid_option,
            invalid_option,
        ],
    )

    result = calculate_option_chain_iv(
        option_chain=chain,
        risk_free_rate=0.06,
    )

    assert len(result.points) == 1
    assert result.failed_contracts == 1


def test_calculate_option_chain_iv_rejects_all_failed_contracts() -> None:
    invalid_option = create_option(
        "CALL",
        1900.0,
        0.0,
        0.0,
    )

    chain = OptionChain(
        underlying="INFY",
        timestamp=date(2026, 9, 1),
        underlying_price=1900.0,
        options=[invalid_option],
    )

    with pytest.raises(
        ValueError,
        match="No option contracts produced a valid implied volatility",
    ):
        calculate_option_chain_iv(
            option_chain=chain,
            risk_free_rate=0.06,
        )


def test_average_chain_iv() -> None:
    chain = create_chain()

    result = calculate_option_chain_iv(
        option_chain=chain,
        risk_free_rate=0.06,
    )

    average = average_chain_iv(result)

    assert average > 0

    expected = sum(
        point.implied_volatility
        for point in result.points
    ) / len(result.points)

    assert average == pytest.approx(expected)


def test_average_chain_iv_rejects_empty_result() -> None:
    result = OptionChainIVResult(
        points=[],
        failed_contracts=0,
    )

    with pytest.raises(
        ValueError,
        match="Cannot calculate average IV without points",
    ):
        average_chain_iv(result)


def test_filter_by_expiration() -> None:
    chain = create_chain()

    result = calculate_option_chain_iv(
        option_chain=chain,
        risk_free_rate=0.06,
    )

    filtered = filter_chain_iv_by_expiration(
        result,
        date(2026, 12, 31),
    )

    assert len(filtered) == 4


def test_filter_by_option_type() -> None:
    chain = create_chain()

    result = calculate_option_chain_iv(
        option_chain=chain,
        risk_free_rate=0.06,
    )

    calls = filter_chain_iv_by_option_type(
        result,
        "call",
    )

    puts = filter_chain_iv_by_option_type(
        result,
        "PUT",
    )

    assert len(calls) == 2
    assert len(puts) == 2
    assert all(point.option_type == "CALL" for point in calls)
    assert all(point.option_type == "PUT" for point in puts)


def test_filter_by_option_type_rejects_invalid_type() -> None:
    chain = create_chain()

    result = calculate_option_chain_iv(
        option_chain=chain,
        risk_free_rate=0.06,
    )

    with pytest.raises(
        ValueError,
        match="Option type must be CALL or PUT",
    ):
        filter_chain_iv_by_option_type(
            result,
            "XYZ",
        )