import pytest

from app.pricing.black_scholes import (
    black_scholes_call,
    black_scholes_put,
)
from app.pricing.volatility_surface import (
    OptionObservation,
    VolatilityPoint,
    VolatilitySmile,
    VolatilityTermStructurePoint,
    build_volatility_surface,
    calculate_skew,
    calculate_term_structure,
    calculate_volatility_point,
    calculate_volatility_smile,
    group_by_expiry,
    group_by_strike,
    interpolate_implied_volatility,
)


SPOT = 100.0
RATE = 0.05
VOLATILITY = 0.20


def test_calculate_call_volatility_point() -> None:
    market_price = black_scholes_call(
        SPOT,
        100.0,
        1.0,
        RATE,
        VOLATILITY,
    )

    observation = OptionObservation(
        strike_price=100.0,
        time_to_expiry=1.0,
        market_price=market_price,
        option_type="CALL",
    )

    point = calculate_volatility_point(
        spot_price=SPOT,
        risk_free_rate=RATE,
        observation=observation,
    )

    assert isinstance(point, VolatilityPoint)
    assert point.strike_price == 100.0
    assert point.time_to_expiry == 1.0
    assert point.option_type == "CALL"
    assert point.implied_volatility == pytest.approx(
        VOLATILITY,
        abs=1e-6,
    )


def test_calculate_put_volatility_point() -> None:
    market_price = black_scholes_put(
        SPOT,
        100.0,
        1.0,
        RATE,
        VOLATILITY,
    )

    observation = OptionObservation(
        strike_price=100.0,
        time_to_expiry=1.0,
        market_price=market_price,
        option_type="PUT",
    )

    point = calculate_volatility_point(
        spot_price=SPOT,
        risk_free_rate=RATE,
        observation=observation,
    )

    assert point.option_type == "PUT"
    assert point.implied_volatility == pytest.approx(
        VOLATILITY,
        abs=1e-6,
    )


def test_lowercase_option_type_is_normalized() -> None:
    market_price = black_scholes_call(
        SPOT,
        100.0,
        1.0,
        RATE,
        VOLATILITY,
    )

    observation = OptionObservation(
        strike_price=100.0,
        time_to_expiry=1.0,
        market_price=market_price,
        option_type="call",
    )

    point = calculate_volatility_point(
        SPOT,
        RATE,
        observation,
    )

    assert point.option_type == "CALL"


def test_build_surface_from_multiple_observations() -> None:
    observations = [
        OptionObservation(
            strike_price=90.0,
            time_to_expiry=0.5,
            market_price=black_scholes_call(
                SPOT,
                90.0,
                0.5,
                RATE,
                VOLATILITY,
            ),
            option_type="CALL",
        ),
        OptionObservation(
            strike_price=100.0,
            time_to_expiry=0.5,
            market_price=black_scholes_call(
                SPOT,
                100.0,
                0.5,
                RATE,
                VOLATILITY,
            ),
            option_type="CALL",
        ),
        OptionObservation(
            strike_price=110.0,
            time_to_expiry=0.5,
            market_price=black_scholes_call(
                SPOT,
                110.0,
                0.5,
                RATE,
                VOLATILITY,
            ),
            option_type="CALL",
        ),
        OptionObservation(
            strike_price=90.0,
            time_to_expiry=1.0,
            market_price=black_scholes_call(
                SPOT,
                90.0,
                1.0,
                RATE,
                VOLATILITY,
            ),
            option_type="CALL",
        ),
        OptionObservation(
            strike_price=100.0,
            time_to_expiry=1.0,
            market_price=black_scholes_call(
                SPOT,
                100.0,
                1.0,
                RATE,
                VOLATILITY,
            ),
            option_type="CALL",
        ),
        OptionObservation(
            strike_price=110.0,
            time_to_expiry=1.0,
            market_price=black_scholes_call(
                SPOT,
                110.0,
                1.0,
                RATE,
                VOLATILITY,
            ),
            option_type="CALL",
        ),
    ]

    points = build_volatility_surface(
        spot_price=SPOT,
        risk_free_rate=RATE,
        observations=observations,
    )

    assert len(points) == 6

    for point in points:
        assert point.implied_volatility == pytest.approx(
            VOLATILITY,
            abs=1e-6,
        )


def test_group_by_expiry() -> None:
    observations = [
        OptionObservation(
            strike_price=110.0,
            time_to_expiry=1.0,
            market_price=black_scholes_call(
                SPOT,
                110.0,
                1.0,
                RATE,
                VOLATILITY,
            ),
            option_type="CALL",
        ),
        OptionObservation(
            strike_price=90.0,
            time_to_expiry=0.5,
            market_price=black_scholes_call(
                SPOT,
                90.0,
                0.5,
                RATE,
                VOLATILITY,
            ),
            option_type="CALL",
        ),
        OptionObservation(
            strike_price=100.0,
            time_to_expiry=1.0,
            market_price=black_scholes_call(
                SPOT,
                100.0,
                1.0,
                RATE,
                VOLATILITY,
            ),
            option_type="CALL",
        ),
    ]

    points = build_volatility_surface(
        SPOT,
        RATE,
        observations,
    )

    grouped = group_by_expiry(points)

    assert list(grouped.keys()) == [0.5, 1.0]
    assert [
        point.strike_price
        for point in grouped[1.0]
    ] == [100.0, 110.0]


def test_group_by_strike() -> None:
    observations = [
        OptionObservation(
            strike_price=100.0,
            time_to_expiry=1.0,
            market_price=black_scholes_call(
                SPOT,
                100.0,
                1.0,
                RATE,
                VOLATILITY,
            ),
            option_type="CALL",
        ),
        OptionObservation(
            strike_price=100.0,
            time_to_expiry=0.5,
            market_price=black_scholes_call(
                SPOT,
                100.0,
                0.5,
                RATE,
                VOLATILITY,
            ),
            option_type="CALL",
        ),
        OptionObservation(
            strike_price=90.0,
            time_to_expiry=1.0,
            market_price=black_scholes_call(
                SPOT,
                90.0,
                1.0,
                RATE,
                VOLATILITY,
            ),
            option_type="CALL",
        ),
    ]

    points = build_volatility_surface(
        SPOT,
        RATE,
        observations,
    )

    grouped = group_by_strike(points)

    assert list(grouped.keys()) == [90.0, 100.0]
    assert [
        point.time_to_expiry
        for point in grouped[100.0]
    ] == [0.5, 1.0]


def _build_test_surface() -> list[VolatilityPoint]:
    observations = []

    volatility_by_strike = {
        90.0: 0.25,
        100.0: 0.20,
        110.0: 0.23,
    }

    volatility_by_expiry = {
        0.5: 1.0,
        1.0: 0.95,
    }

    for expiry, expiry_multiplier in volatility_by_expiry.items():
        for strike, base_volatility in volatility_by_strike.items():
            volatility = (
                base_volatility
                * expiry_multiplier
            )

            market_price = black_scholes_call(
                SPOT,
                strike,
                expiry,
                RATE,
                volatility,
            )

            observations.append(
                OptionObservation(
                    strike_price=strike,
                    time_to_expiry=expiry,
                    market_price=market_price,
                    option_type="CALL",
                )
            )

    return build_volatility_surface(
        SPOT,
        RATE,
        observations,
    )


def test_calculate_volatility_smile() -> None:
    points = _build_test_surface()

    smile = calculate_volatility_smile(
        points,
        time_to_expiry=0.5,
    )

    assert isinstance(smile, VolatilitySmile)
    assert smile.time_to_expiry == 0.5

    assert [
        point.strike_price
        for point in smile.points
    ] == [90.0, 100.0, 110.0]


def test_volatility_smile_contains_correct_ivs() -> None:
    points = _build_test_surface()

    smile = calculate_volatility_smile(
        points,
        time_to_expiry=0.5,
    )

    assert smile.points[0].implied_volatility == pytest.approx(
        0.25,
        abs=1e-6,
    )

    assert smile.points[1].implied_volatility == pytest.approx(
        0.20,
        abs=1e-6,
    )

    assert smile.points[2].implied_volatility == pytest.approx(
        0.23,
        abs=1e-6,
    )


def test_calculate_skew() -> None:
    points = _build_test_surface()

    skew = calculate_skew(
        points=points,
        time_to_expiry=0.5,
        lower_strike=90.0,
        upper_strike=110.0,
    )

    expected_skew = (
        0.23 - 0.25
    ) / (
        110.0 - 90.0
    )

    assert skew == pytest.approx(
        expected_skew,
        abs=1e-6,
    )


def test_negative_skew_is_detected() -> None:
    points = _build_test_surface()

    skew = calculate_skew(
        points=points,
        time_to_expiry=0.5,
        lower_strike=90.0,
        upper_strike=100.0,
    )

    assert skew < 0.0


def test_calculate_term_structure() -> None:
    points = _build_test_surface()

    term_structure = calculate_term_structure(
        points=points,
        strike_price=100.0,
    )

    assert all(
        isinstance(
            point,
            VolatilityTermStructurePoint,
        )
        for point in term_structure
    )

    assert [
        point.time_to_expiry
        for point in term_structure
    ] == [0.5, 1.0]

    assert term_structure[0].implied_volatility == pytest.approx(
        0.20,
        abs=1e-6,
    )

    assert term_structure[1].implied_volatility == pytest.approx(
        0.19,
        abs=1e-6,
    )


def test_interpolation_at_exact_point() -> None:
    points = _build_test_surface()

    volatility = interpolate_implied_volatility(
        points,
        strike_price=100.0,
        time_to_expiry=0.5,
    )

    assert volatility == pytest.approx(
        0.20,
        abs=1e-6,
    )


def test_interpolation_between_strikes() -> None:
    points = _build_test_surface()

    volatility = interpolate_implied_volatility(
        points,
        strike_price=95.0,
        time_to_expiry=0.5,
    )

    expected = (
        0.25 + 0.20
    ) / 2.0

    assert volatility == pytest.approx(
        expected,
        abs=1e-6,
    )


def test_interpolation_between_expiries() -> None:
    points = _build_test_surface()

    volatility = interpolate_implied_volatility(
        points,
        strike_price=100.0,
        time_to_expiry=0.75,
    )

    expected = (
        0.20 + 0.19
    ) / 2.0

    assert volatility == pytest.approx(
        expected,
        abs=1e-6,
    )


def test_bilinear_interpolation() -> None:
    points = _build_test_surface()

    volatility = interpolate_implied_volatility(
        points,
        strike_price=95.0,
        time_to_expiry=0.75,
    )

    lower_expiry_iv = (
        0.25 + 0.20
    ) / 2.0

    upper_expiry_iv = (
        0.2375 + 0.19
    ) / 2.0

    expected = (
        lower_expiry_iv
        + upper_expiry_iv
    ) / 2.0

    assert volatility == pytest.approx(
        expected,
        abs=1e-6,
    )


def test_interpolation_is_case_insensitive_for_option_type() -> None:
    points = _build_test_surface()

    volatility = interpolate_implied_volatility(
        points,
        strike_price=100.0,
        time_to_expiry=0.75,
        option_type="call",
    )

    assert volatility == pytest.approx(
        0.195,
        abs=1e-6,
    )


def test_interpolation_rejects_strike_below_range() -> None:
    points = _build_test_surface()

    with pytest.raises(ValueError):
        interpolate_implied_volatility(
            points,
            strike_price=80.0,
            time_to_expiry=0.75,
        )


def test_interpolation_rejects_strike_above_range() -> None:
    points = _build_test_surface()

    with pytest.raises(ValueError):
        interpolate_implied_volatility(
            points,
            strike_price=120.0,
            time_to_expiry=0.75,
        )


def test_interpolation_rejects_expiry_below_range() -> None:
    points = _build_test_surface()

    with pytest.raises(ValueError):
        interpolate_implied_volatility(
            points,
            strike_price=100.0,
            time_to_expiry=0.25,
        )


def test_interpolation_rejects_expiry_above_range() -> None:
    points = _build_test_surface()

    with pytest.raises(ValueError):
        interpolate_implied_volatility(
            points,
            strike_price=100.0,
            time_to_expiry=2.0,
        )


def test_interpolation_rejects_empty_surface() -> None:
    with pytest.raises(ValueError):
        interpolate_implied_volatility(
            [],
            strike_price=100.0,
            time_to_expiry=1.0,
        )


def test_interpolation_rejects_missing_grid_point() -> None:
    points = _build_test_surface()

    incomplete_points = [
        point
        for point in points
        if not (
            point.strike_price == 110.0
            and point.time_to_expiry == 1.0
        )
    ]

    with pytest.raises(ValueError):
        interpolate_implied_volatility(
            incomplete_points,
            strike_price=105.0,
            time_to_expiry=0.75,
        )


def test_smile_requires_existing_expiry() -> None:
    points = _build_test_surface()

    with pytest.raises(ValueError):
        calculate_volatility_smile(
            points,
            time_to_expiry=2.0,
        )


def test_term_structure_requires_existing_strike() -> None:
    points = _build_test_surface()

    with pytest.raises(ValueError):
        calculate_term_structure(
            points,
            strike_price=120.0,
        )


def test_skew_requires_existing_strikes() -> None:
    points = _build_test_surface()

    with pytest.raises(ValueError):
        calculate_skew(
            points,
            time_to_expiry=0.5,
            lower_strike=80.0,
            upper_strike=110.0,
        )


@pytest.mark.parametrize(
    "observation",
    [
        OptionObservation(
            strike_price=0.0,
            time_to_expiry=1.0,
            market_price=10.0,
            option_type="CALL",
        ),
        OptionObservation(
            strike_price=100.0,
            time_to_expiry=0.0,
            market_price=10.0,
            option_type="CALL",
        ),
        OptionObservation(
            strike_price=100.0,
            time_to_expiry=1.0,
            market_price=0.0,
            option_type="CALL",
        ),
        OptionObservation(
            strike_price=100.0,
            time_to_expiry=1.0,
            market_price=10.0,
            option_type="INVALID",
        ),
    ],
)
def test_invalid_observation(
    observation: OptionObservation,
) -> None:
    with pytest.raises(ValueError):
        calculate_volatility_point(
            SPOT,
            RATE,
            observation,
        )


def test_invalid_spot_price() -> None:
    observation = OptionObservation(
        strike_price=100.0,
        time_to_expiry=1.0,
        market_price=10.0,
        option_type="CALL",
    )

    with pytest.raises(ValueError):
        build_volatility_surface(
            spot_price=0.0,
            risk_free_rate=RATE,
            observations=[observation],
        )


def test_empty_observations() -> None:
    with pytest.raises(ValueError):
        build_volatility_surface(
            spot_price=SPOT,
            risk_free_rate=RATE,
            observations=[],
        )


def test_invalid_skew_strike_order() -> None:
    points = _build_test_surface()

    with pytest.raises(ValueError):
        calculate_skew(
            points,
            time_to_expiry=0.5,
            lower_strike=110.0,
            upper_strike=90.0,
        )