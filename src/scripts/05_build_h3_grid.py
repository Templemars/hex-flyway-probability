#!/usr/bin/env python3
"""
Build the first H3 benchmark grid at the agreed resolution.

Purpose
-------
Create a clean H3-based benchmark grid from the cleaned environmental table.

Current design choices already agreed in discussion:
- use the cleaned benchmark wind table as the spatial support reference
- use H3 resolution 3
- keep the implementation simple and readable
- report outputs clearly

Current scope
-------------
1. Read the cleaned benchmark wind table
2. Convert each benchmark point to an H3 cell at resolution 3
3. Keep unique H3 cells only
4. Compute simple centroids and average-area metadata
5. Write the resulting H3 grid table

This step does not yet:
- assign environmental values to H3 cells
- build adjacency tables
- run any path model
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import h3


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "benchmark_tables" / "spring_wind_clean.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_grid_res3_from_benchmark.csv"
H3_RESOLUTION = 3


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    # Convert each benchmark grid point to an H3 cell at the agreed resolution.
    # We use the point centers from the benchmark support as a simple first mapping.
    df = df[["lon", "lat"]].drop_duplicates().copy()
    df["h3_cell"] = [h3.latlng_to_cell(lat, lon, H3_RESOLUTION) for lon, lat in zip(df["lon"], df["lat"])]

    # Keep one row per unique H3 cell.
    unique_cells = pd.DataFrame({"h3_cell": sorted(df["h3_cell"].unique())})

    # Store simple geometric summaries for later use.
    centroids = unique_cells["h3_cell"].apply(h3.cell_to_latlng)
    unique_cells["lat"] = [lat for lat, lon in centroids]
    unique_cells["lon"] = [lon for lat, lon in centroids]
    unique_cells["resolution"] = H3_RESOLUTION
    unique_cells["avg_hex_area_km2"] = h3.average_hexagon_area(H3_RESOLUTION, unit="km^2")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    unique_cells.to_csv(OUTPUT_PATH, index=False)

    print("Built H3 benchmark grid")
    print(f"rows: {len(unique_cells)}")
    print(f"resolution: {H3_RESOLUTION}")
    print(f"average H3 hex area (km^2): {h3.average_hexagon_area(H3_RESOLUTION, unit='km^2'):.2f}")
    print(f"written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
