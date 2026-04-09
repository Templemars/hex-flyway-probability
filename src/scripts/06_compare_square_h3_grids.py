#!/usr/bin/env python3
"""
Compare the square and H3 benchmark grids at a basic geometric level.

Purpose
-------
Before assigning environmental values to the H3 support, compare the two grid
geometries directly so we understand the baseline difference in support.

Current scope
-------------
1. Read the square-grid and H3-grid tables
2. Summarize cell counts and simple area quantities
3. Write a compact comparison table

This script intentionally stays simple and report-oriented.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SQUARE_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "square_grid_from_benchmark.csv"
H3_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_grid_res3_from_benchmark.csv"
OUTPUT_PATH = PROJECT_ROOT / "results" / "tables" / "06_compare_square_h3_grids_summary.csv"

EARTH_RADIUS_KM = 6371.0088


def latlon_cell_area_km2(lat_center_deg: float, dlat_deg: float = 1.0, dlon_deg: float = 1.0) -> float:
    """Area of a lat-lon cell on a sphere in km²."""
    lat1 = math.radians(lat_center_deg - dlat_deg / 2.0)
    lat2 = math.radians(lat_center_deg + dlat_deg / 2.0)
    dlon = math.radians(dlon_deg)
    return (EARTH_RADIUS_KM ** 2) * dlon * abs(math.sin(lat2) - math.sin(lat1))


def main() -> None:
    square = pd.read_csv(SQUARE_PATH)
    h3_grid = pd.read_csv(H3_PATH)

    square_areas = square["lat"].apply(latlon_cell_area_km2)

    summary = pd.DataFrame(
        [
            {
                "square_rows": len(square),
                "h3_rows": len(h3_grid),
                "square_mean_area_km2": square_areas.mean(),
                "square_min_area_km2": square_areas.min(),
                "square_max_area_km2": square_areas.max(),
                "h3_avg_area_km2": h3_grid["avg_hex_area_km2"].iloc[0],
                "h3_to_square_mean_area_ratio": h3_grid["avg_hex_area_km2"].iloc[0] / square_areas.mean(),
            }
        ]
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUTPUT_PATH, index=False)

    print("Compared square and H3 benchmark grids")
    print(summary.to_string(index=False))
    print(f"written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
