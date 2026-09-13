from pathlib import Path

import matplotlib.pyplot as plt

from app.pricing.volatility_surface import (
    VolatilityPoint,
    calculate_volatility_smile,
    calculate_term_structure,
    group_by_expiry,
)


def plot_volatility_smile(
    points: list[VolatilityPoint],
    time_to_expiry: float,
    output_path: str | Path | None = None,
) -> None:
    """
    Plot implied volatility against strike for one expiry.
    """

    smile = calculate_volatility_smile(
        points=points,
        time_to_expiry=time_to_expiry,
    )

    strikes = [
        point.strike_price
        for point in smile.points
    ]

    implied_volatilities = [
        point.implied_volatility * 100.0
        for point in smile.points
    ]

    plt.figure()

    plt.plot(
        strikes,
        implied_volatilities,
        marker="o",
    )

    plt.xlabel("Strike Price")
    plt.ylabel("Implied Volatility (%)")
    plt.title(
        f"Volatility Smile - T={time_to_expiry:.2f} Years"
    )
    plt.grid(True)

    if output_path is not None:
        plt.savefig(
            output_path,
            bbox_inches="tight",
        )

    plt.close()


def plot_volatility_term_structure(
    points: list[VolatilityPoint],
    strike_price: float,
    output_path: str | Path | None = None,
) -> None:
    """
    Plot implied volatility against time to expiry
    for one strike price.
    """

    term_structure = calculate_term_structure(
        points=points,
        strike_price=strike_price,
    )

    expiries = [
        point.time_to_expiry
        for point in term_structure
    ]

    implied_volatilities = [
        point.implied_volatility * 100.0
        for point in term_structure
    ]

    plt.figure()

    plt.plot(
        expiries,
        implied_volatilities,
        marker="o",
    )

    plt.xlabel("Time to Expiry (Years)")
    plt.ylabel("Implied Volatility (%)")
    plt.title(
        f"Volatility Term Structure - K={strike_price:.2f}"
    )
    plt.grid(True)

    if output_path is not None:
        plt.savefig(
            output_path,
            bbox_inches="tight",
        )

    plt.close()


def plot_volatility_surface(
    points: list[VolatilityPoint],
    output_path: str | Path | None = None,
) -> None:
    """
    Plot a 3D implied-volatility surface.

    The x-axis represents strike price.
    The y-axis represents time to expiry.
    The z-axis represents implied volatility.
    """

    grouped = group_by_expiry(points)

    if not grouped:
        raise ValueError(
            "At least one volatility point is required."
        )

    expiries = sorted(grouped.keys())

    strikes = sorted(
        {
            point.strike_price
            for point in points
        }
    )

    volatility_lookup = {
        (
            point.time_to_expiry,
            point.strike_price,
        ): point.implied_volatility * 100.0
        for point in points
    }

    missing_points = [
        (expiry, strike)
        for expiry in expiries
        for strike in strikes
        if (expiry, strike) not in volatility_lookup
    ]

    if missing_points:
        raise ValueError(
            "Volatility surface must contain a complete grid "
            "for 3D visualization."
        )

    volatility_matrix = [
        [
            volatility_lookup[(expiry, strike)]
            for strike in strikes
        ]
        for expiry in expiries
    ]

    figure = plt.figure()
    axis = figure.add_subplot(
        111,
        projection="3d",
    )

    x_values, y_values = [], []
    z_values = []

    for expiry_index, expiry in enumerate(expiries):
        for strike_index, strike in enumerate(strikes):
            x_values.append(strike)
            y_values.append(expiry)
            z_values.append(
                volatility_matrix[
                    expiry_index
                ][strike_index]
            )

    axis.plot_trisurf(
        x_values,
        y_values,
        z_values,
    )

    axis.set_xlabel("Strike Price")
    axis.set_ylabel("Time to Expiry (Years)")
    axis.set_zlabel("Implied Volatility (%)")
    axis.set_title("Implied Volatility Surface")

    if output_path is not None:
        plt.savefig(
            output_path,
            bbox_inches="tight",
        )

    plt.close()