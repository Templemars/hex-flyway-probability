#!/usr/bin/env python3
"""
Build the first H3 edge-geometry table.

Purpose
-------
Create a transparent directed edge table for the H3 graph, containing the
basic geometric information needed before environmental movement components are
constructed.

Current scope
-------------
1. Read the H3 grid table
2. Build directed source-target neighbor edges
3. Compute source/target coordinates
4. Compute edge distance and initial movement bearing
5. Write a clean edge-geometry table

This is intentionally a geometry-only step.
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import h3


PROJECT_ROOT = Path(__file__).resolve().parents[2]
H3_GRID_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_grid_res3_from_benchmark.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_edge_geometry_res3.csv"
EARTH_RADIUS_KM = 6371.0088


def haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Great-circle distance between two lon/lat points in km."""
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_RADIUS_KM * c


def initial_bearing_deg(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Initial bearing from source point to target point in degrees."""
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def main() -> None:
    h3_grid = pd.read_csv(H3_GRID_PATH)
    coord_lookup = h3_grid.set_index("h3_cell")[["lon", "lat"]].to_dict("index")
    valid_cells = set(h3_grid["h3_cell"])

    edge_rows = []
    for source in h3_grid["h3_cell"]:
        source_lon = coord_lookup[source]["lon"]
        source_lat = coord_lookup[source]["lat"]

        # Keep only neighbors that are also present in the benchmark H3 grid.
        neighbors = sorted([cell for cell in h3.grid_ring(source, 1) if cell in valid_cells])

        for target in neighbors:
            target_lon = coord_lookup[target]["lon"]
            target_lat = coord_lookup[target]["lat"]
            edge_rows.append(
                {
                    "source_h3": source,
                    "target_h3": target,
                    "source_lon": source_lon,
                    "source_lat": source_lat,
                    "target_lon": target_lon,
                    "target_lat": target_lat,
                    "edge_distance_km": haversine_km(source_lon, source_lat, target_lon, target_lat),
                    "edge_bearing_deg": initial_bearing_deg(source_lon, source_lat, target_lon, target_lat),
                }
            )

    edges = pd.DataFrame(edge_rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    edges.to_csv(OUTPUT_PATH, index=False)

    print("Built H3 edge-geometry table")
    print(f"rows: {len(edges)}")
    print(f"written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
