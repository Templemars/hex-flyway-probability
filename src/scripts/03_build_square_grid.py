#!/usr/bin/env python3
"""
Build a simple square benchmark grid from the cleaned environmental tables.

Purpose
-------
This is the first grid-construction step for the new project.

We keep it deliberately simple:
- read the cleaned benchmark wind table with pandas
- infer the existing benchmark coordinate spacing
- write out a square-grid table representing the benchmark support

This first version does not yet perform interpolation or modelling.
It simply defines the square-grid geometry that later steps will use.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "benchmark_tables" / "spring_wind_clean.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "square_grid_from_benchmark.csv"


def infer_spacing(values: pd.Series) -> float:
    """Infer grid spacing from sorted unique coordinate values.

    We use the minimum positive difference as a simple and transparent estimate.
    """
    unique_values = sorted(values.dropna().unique())
    diffs = []

    for left, right in zip(unique_values[:-1], unique_values[1:]):
        diff = right - left
        if diff > 0:
            diffs.append(diff)

    if not diffs:
        raise ValueError("Could not infer spacing from coordinate values.")

    return float(min(diffs))


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    lon_spacing = infer_spacing(df["lon"])
    lat_spacing = infer_spacing(df["lat"])

    square_grid = (
        df[["lon", "lat"]]
        .drop_duplicates()
        .sort_values(["lat", "lon"])
        .reset_index(drop=True)
    )
    square_grid["lon_spacing_deg"] = lon_spacing
    square_grid["lat_spacing_deg"] = lat_spacing

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    square_grid.to_csv(OUTPUT_PATH, index=False)

    print("Built square benchmark grid")
    print(f"rows: {len(square_grid)}")
    print(f"lon spacing (deg): {lon_spacing}")
    print(f"lat spacing (deg): {lat_spacing}")
    print(f"written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
