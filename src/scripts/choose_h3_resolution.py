#!/usr/bin/env python3
"""
Choose an H3 resolution that is roughly comparable to the benchmark 1° lat-lon grid.

Purpose
-------
The benchmark environmental CSVs are on a 1° global lat-lon grid.
For the hex-grid sequel, we want a simple, reproducible rule for choosing an H3
resolution with a roughly comparable global mean cell area.

Approach
--------
1. Estimate the global-mean area of a 1° x 1° cell.
2. Query average H3 cell areas across candidate resolutions.
3. Report the closest H3 resolution.

Notes
-----
- We use a spherical Earth approximation for the 1° cell area estimate.
- We use a global mean because the user wants a choice reusable for future
  Atlantic and Pacific work.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import h3


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_resolution_comparison.csv"


EARTH_RADIUS_KM = 6371.0088


def latlon_cell_area_km2(lat_center_deg: float, dlat_deg: float = 1.0, dlon_deg: float = 1.0) -> float:
    """Area of a lat-lon cell on a sphere in km².

    Formula uses the spherical quadrilateral area:
        A = R^2 * dlon_rad * (sin(lat2) - sin(lat1))
    """
    lat1 = math.radians(lat_center_deg - dlat_deg / 2.0)
    lat2 = math.radians(lat_center_deg + dlat_deg / 2.0)
    dlon = math.radians(dlon_deg)
    return (EARTH_RADIUS_KM ** 2) * dlon * abs(math.sin(lat2) - math.sin(lat1))


def global_mean_one_degree_area_km2() -> float:
    """Compute the global-mean area of a 1° x 1° grid cell.

    The benchmark grid centers run from -89.5 to 89.5 by 1 degree.
    We average across latitude bands because all longitude cells at a given
    latitude have the same area.
    """
    lat_centers = np.arange(-89.5, 90.0, 1.0)
    areas = [latlon_cell_area_km2(lat) for lat in lat_centers]
    return float(np.mean(areas))


def main() -> None:
    target_area = global_mean_one_degree_area_km2()

    rows = []
    for resolution in range(0, 16):
        h3_area = h3.average_hexagon_area(resolution, unit="km^2")
        rows.append(
            {
                "resolution": resolution,
                "h3_avg_area_km2": h3_area,
                "target_global_mean_1deg_area_km2": target_area,
                "abs_difference_km2": abs(h3_area - target_area),
            }
        )

    df = pd.DataFrame(rows).sort_values("abs_difference_km2").reset_index(drop=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    best = df.iloc[0]

    print("H3 resolution comparison against global-mean 1° cell area")
    print(f"Target global-mean 1° area: {target_area:.2f} km^2")
    print()
    print("Top candidate resolutions:")
    print(df.head(5).to_string(index=False))
    print()
    print(
        "Selected best match: "
        f"resolution {int(best['resolution'])} "
        f"with average area {best['h3_avg_area_km2']:.2f} km^2"
    )
    print(f"Saved full comparison to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
