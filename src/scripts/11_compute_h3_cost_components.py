#!/usr/bin/env python3
"""
Compute raw and standardized H3 movement-cost components on directed edges.

Purpose
-------
This script constructs the first full component table for the H3 sequel.
It follows the published 2025 logic where possible, while incorporating the
agreed refinement that distance is based on true H3 edge length.

Current scope
-------------
1. Read the enriched directed H3 edge table
2. Compute raw edge-level movement components
3. Standardize components using a P99-based scaling philosophy
4. Write a transparent component table

Component ordering for the sequel:
- a = wind
- b = crosswind
- c = distance
- d = food
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EDGE_ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_edge_environment_res3.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_edge_cost_components_res3.csv"


def percentile_99(series: pd.Series) -> float:
    clean = series.dropna().to_numpy()
    return float(np.percentile(clean, 99))


def percentile_50(series: pd.Series) -> float:
    clean = series.dropna().to_numpy()
    return float(np.percentile(clean, 50))


def standardize_to_100(series: pd.Series) -> pd.Series:
    p99 = percentile_99(series)
    if p99 == 0:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return 100.0 * series / p99


def bearing_to_unit_vector(bearing_deg: pd.Series) -> tuple[pd.Series, pd.Series]:
    rad = np.deg2rad(bearing_deg)
    east = np.sin(rad)
    north = np.cos(rad)
    return pd.Series(east, index=bearing_deg.index), pd.Series(north, index=bearing_deg.index)


def compute_food_cost(source_chla: pd.Series) -> pd.Series:
    """Apply the published 2025 chlorophyll treatment.

    Paper logic retained:
    - use log-transformed chlorophyll
    - cap high-productivity cells so all chlor_a > 0.1 mg/m^3 are maximally good
    - convert the transformed value into a positive cost distance from that optimum
    """
    safe = source_chla.copy()
    safe = safe.where(safe > 0)
    log_term = np.log(safe)
    capped = log_term.where(log_term <= -1, -1)
    food_cost = np.abs(capped + 1)
    return pd.Series(food_cost, index=source_chla.index)


def main() -> None:
    df = pd.read_csv(EDGE_ENV_PATH)

    # Movement direction as an east/north unit vector.
    move_east, move_north = bearing_to_unit_vector(df["edge_bearing_deg"])

    # Raw wind support and crosswind, using source-cell wind components.
    # Dot product gives parallel support along the movement direction.
    windsupport = df["source_u10"] * move_east + df["source_v10"] * move_north
    p99_windsupport = percentile_99(windsupport)
    parallel_wind_cost_raw = np.abs(windsupport - p99_windsupport)

    # Magnitude of the perpendicular wind component.
    crosswind_raw = np.abs(df["source_u10"] * move_north - df["source_v10"] * move_east)

    # Distance refinement for H3: true edge length rather than constant per-step proxy.
    distance_cost_raw = df["edge_distance_km"]

    # Food cost follows the published chlorophyll logic.
    food_cost_raw = compute_food_cost(df["source_chlor_a"])

    out = df.copy()
    out["windsupport_raw"] = windsupport
    out["parallel_wind_cost_raw"] = parallel_wind_cost_raw
    out["crosswind_cost_raw"] = crosswind_raw
    out["distance_cost_raw"] = distance_cost_raw
    out["food_cost_raw"] = food_cost_raw

    # Published-style P99 standardization philosophy.
    out["w_cost"] = standardize_to_100(out["parallel_wind_cost_raw"])
    out["c_cost"] = standardize_to_100(out["crosswind_cost_raw"])
    out["d_cost"] = standardize_to_100(out["distance_cost_raw"])
    out["f_cost"] = standardize_to_100(out["food_cost_raw"])

    # Keep a reference to the old paper's distance heuristic for comparison.
    out["legacy_constant_distance_reference"] = percentile_50(out["w_cost"])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_PATH, index=False)

    print("Computed H3 edge cost components")
    print(f"rows: {len(out)}")
    print(f"written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
