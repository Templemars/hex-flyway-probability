#!/usr/bin/env python3
"""
Assign environmental values from the benchmark 1° grid to the H3 grid.

Purpose
-------
Use the agreed first prototype method:
- compute H3 centroids
- sample the benchmark environmental fields at those centroids
- use nearest-neighbor assignment from the 1° benchmark support

Current scope
-------------
1. Read the cleaned benchmark wind and chlorophyll tables
2. Read the H3 grid table
3. For each H3 centroid, assign the nearest benchmark point
4. Build one H3 environmental table

Notes
-----
- This is a simple prototype method, not exact conservative remapping.
- Wind direction is not treated as a primary field here.
- `u10` and `v10` are treated as the primary wind variables.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WIND_PATH = PROJECT_ROOT / "data" / "processed" / "benchmark_tables" / "spring_wind_clean.csv"
CHLA_PATH = PROJECT_ROOT / "data" / "processed" / "benchmark_tables" / "spring_chla_clean.csv"
H3_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_grid_res3_from_benchmark.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_environment_res3.csv"


def nearest_index(target_lon: float, target_lat: float, source_lon: np.ndarray, source_lat: np.ndarray) -> int:
    """Return the index of the nearest benchmark point in simple lon-lat space.

    For the first prototype, we keep this intentionally simple and transparent.
    A more geodetically careful method can be added later if necessary.
    """
    d2 = (source_lon - target_lon) ** 2 + (source_lat - target_lat) ** 2
    return int(np.argmin(d2))


def main() -> None:
    wind = pd.read_csv(WIND_PATH)
    chla = pd.read_csv(CHLA_PATH)
    h3_grid = pd.read_csv(H3_PATH)

    wind_lon = wind["lon"].to_numpy()
    wind_lat = wind["lat"].to_numpy()
    chla_lon = chla["lon"].to_numpy()
    chla_lat = chla["lat"].to_numpy()

    records = []
    for row in h3_grid.itertuples(index=False):
        wind_i = nearest_index(row.lon, row.lat, wind_lon, wind_lat)
        chla_i = nearest_index(row.lon, row.lat, chla_lon, chla_lat)

        wind_row = wind.iloc[wind_i]
        chla_row = chla.iloc[chla_i]

        records.append(
            {
                "h3_cell": row.h3_cell,
                "lon": row.lon,
                "lat": row.lat,
                "resolution": row.resolution,
                "avg_hex_area_km2": row.avg_hex_area_km2,
                "source_wind_lon": wind_row["lon"],
                "source_wind_lat": wind_row["lat"],
                "u10": wind_row["u10"],
                "v10": wind_row["v10"],
                "speed": wind_row["speed"],
                "source_chla_lon": chla_row["lon"],
                "source_chla_lat": chla_row["lat"],
                "chlor_a": chla_row["chlor_a"],
            }
        )

    out = pd.DataFrame(records)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_PATH, index=False)

    print("Assigned benchmark environmental values to H3 grid")
    print(f"rows: {len(out)}")
    print(f"written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
