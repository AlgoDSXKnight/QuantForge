from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from app.pricing.black_scholes import black_scholes_call
from app.pricing.volatility_surface import (
    OptionObservation,
    VolatilityPoint,
    build_volatility_surface,
)
from app.pricing.volatility_visualization import (
    plot_volatility_smile,
    plot_volatility_surface,
    plot_volatility_term_structure,
)


SPOT = 100.0
RATE = 0.05


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
        spot_price=SPOT,
        risk_free_rate=RATE,
        observations=observations,
    )


def test_plot_volatility_smile_creates_file(
    tmp_path: Path,
) -> None:
    points = _build_test_surface()

    output_path = (
        tmp_path / "volatility_smile.png"
    )

    plot_volatility_smile(
        points=points,
        time_to_expiry=0.5,
        output_path=output_path,
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_plot_volatility_term_structure_creates_file(
    tmp_path: Path,
) -> None:
    points = _build_test_surface()

    output_path = (
        tmp_path / "term_structure.png"
    )

    plot_volatility_term_structure(
        points=points,
        strike_price=100.0,
        output_path=output_path,
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_plot_volatility_surface_creates_file(
    tmp_path: Path,
) -> None:
    points = _build_test_surface()

    output_path = (
        tmp_path / "volatility_surface.png"
    )

    plot_volatility_surface(
        points=points,
        output_path=output_path,
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_plots_work_without_output_path() -> None:
    points = _build_test_surface()

    plot_volatility_smile(
        points=points,
        time_to_expiry=0.5,
    )

    plot_volatility_term_structure(
        points=points,
        strike_price=100.0,
    )

    plot_volatility_surface(
        points=points,
    )


def test_surface_plot_rejects_incomplete_grid(
    tmp_path: Path,
) -> None:
    points = _build_test_surface()

    incomplete_points = [
        point
        for point in points
        if not (
            point.strike_price == 110.0
            and point.time_to_expiry == 1.0
        )
    ]

    output_path = (
        tmp_path / "invalid_surface.png"
    )

    try:
        plot_volatility_surface(
            points=incomplete_points,
            output_path=output_path,
        )
    except ValueError as error:
        assert (
            "complete grid"
            in str(error)
        )
    else:
        raise AssertionError(
            "Expected ValueError for incomplete surface."
        )


def test_smile_plot_rejects_missing_expiry() -> None:
    points = _build_test_surface()

    try:
        plot_volatility_smile(
            points=points,
            time_to_expiry=2.0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for missing expiry."
        )


def test_term_structure_plot_rejects_missing_strike() -> None:
    points = _build_test_surface()

    try:
        plot_volatility_term_structure(
            points=points,
            strike_price=120.0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for missing strike."
        )