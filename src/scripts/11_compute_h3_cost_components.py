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

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EDGE_ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_edge_environment_res3.csv"
ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_environment_res3.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_edge_cost_components_res3.csv"
SUMMARY_PATH = PROJECT_ROOT / "results" / "tables" / "11_compute_h3_cost_components_summary.csv"
EXAMPLE_PATH = PROJECT_ROOT / "results" / "tables" / "11_compute_h3_cost_components_example_rows.csv"
REPORT_PATH = PROJECT_ROOT / "results" / "reports" / "11_compute-h3-cost-components.md"
RAW_HIST_PATH = PROJECT_ROOT / "results" / "figures" / "11_raw_component_histograms.png"
STD_HIST_PATH = PROJECT_ROOT / "results" / "figures" / "11_standardized_component_histograms.png"
SCATTER_PATH = PROJECT_ROOT / "results" / "figures" / "11_wind_vs_crosswind_scatter.png"
MAP_WIND_PATH = PROJECT_ROOT / "results" / "figures" / "11_map_parallel_wind_cost_northward.png"
MAP_CROSSWIND_PATH = PROJECT_ROOT / "results" / "figures" / "11_map_crosswind_cost_northward.png"
MAP_DISTANCE_PATH = PROJECT_ROOT / "results" / "figures" / "11_map_distance_cost.png"
MAP_FOOD_PATH = PROJECT_ROOT / "results" / "figures" / "11_map_food_cost.png"


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


def compute_food_cost(source_chla: pd.Series, floor: float | None = None) -> pd.Series:
    """Apply the published 2025 chlorophyll treatment.

    Low-food cells must become high-cost cells.
    To preserve that behavior for zero chlorophyll values, replace non-positive
    values with a small positive floor before taking the logarithm.
    """
    positive = source_chla[source_chla > 0]
    if floor is None:
        floor = float(positive.min()) if len(positive) else 1e-6

    safe = source_chla.clip(lower=floor)
    log_term = np.log(safe)
    capped = log_term.where(log_term <= -1, -1)
    food_cost = np.abs(capped + 1)
    return pd.Series(food_cost, index=source_chla.index)


def draw_component_map(df: pd.DataFrame, value_col: str, output_path: Path, title: str, cmap: str = "viridis") -> None:
    fig, ax = plt.subplots(figsize=(11, 6.5), constrained_layout=True)
    sc = ax.scatter(df["lon"], df["lat"], c=df[value_col], s=10, cmap=cmap, linewidths=0)
    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label(value_col)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def main() -> None:
    df = pd.read_csv(EDGE_ENV_PATH)
    env = pd.read_csv(ENV_PATH)

    # Movement direction as an east/north unit vector.
    move_east, move_north = bearing_to_unit_vector(df["edge_bearing_deg"])

    # Raw wind support and crosswind, using source-cell wind components.
    windsupport = df["source_u10"] * move_east + df["source_v10"] * move_north
    p99_windsupport = percentile_99(windsupport)
    parallel_wind_cost_raw = np.abs(windsupport - p99_windsupport)
    crosswind_raw = np.abs(df["source_u10"] * move_north - df["source_v10"] * move_east)
    distance_cost_raw = df["edge_distance_km"]
    food_cost_raw = compute_food_cost(df["source_chlor_a"])

    out = df.copy()
    out["windsupport_raw"] = windsupport
    out["parallel_wind_cost_raw"] = parallel_wind_cost_raw
    out["crosswind_cost_raw"] = crosswind_raw
    out["distance_cost_raw"] = distance_cost_raw
    out["food_cost_raw"] = food_cost_raw
    out["w_cost"] = standardize_to_100(out["parallel_wind_cost_raw"])
    out["c_cost"] = standardize_to_100(out["crosswind_cost_raw"])
    out["d_cost"] = standardize_to_100(out["distance_cost_raw"])
    out["f_cost"] = standardize_to_100(out["food_cost_raw"])
    out["legacy_constant_distance_reference"] = percentile_50(out["w_cost"])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAW_HIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_PATH, index=False)

    summary_rows = []
    for col in ["parallel_wind_cost_raw", "crosswind_cost_raw", "distance_cost_raw", "food_cost_raw", "w_cost", "c_cost", "d_cost", "f_cost"]:
        s = out[col].dropna()
        summary_rows.append(
            {
                "component": col,
                "count": len(s),
                "mean": s.mean(),
                "median": s.median(),
                "std": s.std(),
                "min": s.min(),
                "max": s.max(),
                "p99": s.quantile(0.99),
            }
        )
    pd.DataFrame(summary_rows).to_csv(SUMMARY_PATH, index=False)
    out.head(40).to_csv(EXAMPLE_PATH, index=False)

    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    for ax, col, title in zip(axes.ravel(), ["parallel_wind_cost_raw", "crosswind_cost_raw", "distance_cost_raw", "food_cost_raw"], ["Raw parallel wind cost", "Raw crosswind cost", "Raw distance cost", "Raw food cost"]):
        ax.hist(out[col].dropna(), bins=40, alpha=0.8)
        ax.set_title(title)
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
    fig.savefig(RAW_HIST_PATH, dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    for ax, col, title in zip(axes.ravel(), ["w_cost", "c_cost", "d_cost", "f_cost"], ["Standardized wind cost", "Standardized crosswind cost", "Standardized distance cost", "Standardized food cost"]):
        ax.hist(out[col].dropna(), bins=40, alpha=0.8)
        ax.set_title(title)
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
    fig.savefig(STD_HIST_PATH, dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 6), constrained_layout=True)
    sample = out[["w_cost", "c_cost"]].dropna().iloc[::20]
    ax.scatter(sample["w_cost"], sample["c_cost"], s=6, alpha=0.4)
    ax.set_title("Standardized wind vs crosswind costs (sampled edges)")
    ax.set_xlabel("w_cost")
    ax.set_ylabel("c_cost")
    fig.savefig(SCATTER_PATH, dpi=150)
    plt.close(fig)

    # Component maps at cell level. For wind maps, use a straight northward heading.
    northward_support = env["v10"]
    northward_parallel_raw = np.abs(northward_support - percentile_99(northward_support))
    northward_crosswind_raw = np.abs(env["u10"])
    env_map = env[["h3_cell", "lon", "lat", "u10", "v10", "chlor_a"]].copy()
    env_map["parallel_wind_cost_northward_raw"] = northward_parallel_raw
    env_map["crosswind_cost_northward_raw"] = northward_crosswind_raw
    env_map["distance_cost_raw"] = out.groupby("source_h3", as_index=False)["distance_cost_raw"].mean()["distance_cost_raw"]
    env_map["food_cost_raw"] = compute_food_cost(env_map["chlor_a"])
    env_map["parallel_wind_cost_northward_std"] = standardize_to_100(env_map["parallel_wind_cost_northward_raw"])
    env_map["crosswind_cost_northward_std"] = standardize_to_100(env_map["crosswind_cost_northward_raw"])
    env_map["distance_cost_std"] = standardize_to_100(env_map["distance_cost_raw"])
    env_map["food_cost_std"] = standardize_to_100(env_map["food_cost_raw"])

    draw_component_map(env_map, "parallel_wind_cost_northward_std", MAP_WIND_PATH, "Parallel wind cost surface for straight northward flight")
    draw_component_map(env_map, "crosswind_cost_northward_std", MAP_CROSSWIND_PATH, "Crosswind cost surface for straight northward flight")
    draw_component_map(env_map, "distance_cost_std", MAP_DISTANCE_PATH, "Distance cost surface (mean outgoing H3 edge distance)")
    draw_component_map(env_map, "food_cost_std", MAP_FOOD_PATH, "Food cost surface from chlorophyll-a")

    legacy_ref = out["legacy_constant_distance_reference"].iloc[0]
    zero_chla_count = int((env["chlor_a"] <= 0).sum())
    positive_floor = float(env.loc[env["chlor_a"] > 0, "chlor_a"].min()) if (env["chlor_a"] > 0).any() else 1e-6
    report = f'''# Compute H3 cost components

## Question
What do the raw and standardized movement-cost components look like on the directed H3 graph, and do they correctly preserve the published food-cost logic?

## Input data
- `data/processed/grids/h3_edge_environment_res3.csv`
- `data/processed/grids/h3_environment_res3.csv`

## Audit result: food-cost correction
The first implementation needed one important correction.

The paper logic implies:
- low chlorophyll should produce high food cost
- high chlorophyll should produce low food cost
- cells above the productivity threshold should collapse toward the same low-cost class

The original implementation preserved that direction for positive chlorophyll values, but treated zero chlorophyll as missing after the log transform. That was not acceptable, because zero-food cells should behave like very poor food cells, not drop out.

The corrected implementation now:
- replaces non-positive chlorophyll with a small positive floor before taking the log
- uses the smallest positive chlorophyll value in the H3 environmental table as that floor
- therefore keeps zero-chlorophyll cells in the cost surface as high-cost cells

Audit values:
- zero or non-positive chlorophyll cells in H3 table: **{zero_chla_count}**
- positive chlorophyll floor used for the log transform: **{positive_floor:.8f}**

## Method
- compute directional edge costs for parallel wind, crosswind, true distance, and food
- standardize each component with the agreed P99-based scaling philosophy
- additionally produce four cell-level component maps for transparency
- for the two wind component maps, assume a bird flying in a straight northward direction everywhere

## Key formulas used
- movement direction comes from the edge bearing for the edge-level table
- wind support is the projection of the source wind vector onto the movement direction
- raw parallel wind cost = distance from `P99(windsupport)`
- raw crosswind cost = magnitude of the wind component perpendicular to movement
- raw distance cost = true H3 edge distance in km
- raw food cost = `|log(chla) + 1|` after capping high-productivity cells and flooring non-positive chlorophyll values for numerical stability
- standardized component cost = `100 * raw_component / P99(raw_component)`

## Outputs
- component table: `data/processed/grids/h3_edge_cost_components_res3.csv`
- summary table: `results/tables/11_compute_h3_cost_components_summary.csv`
- example rows: `results/tables/11_compute_h3_cost_components_example_rows.csv`
- figures:
  - `results/figures/11_raw_component_histograms.png`
  - `results/figures/11_standardized_component_histograms.png`
  - `results/figures/11_wind_vs_crosswind_scatter.png`
  - `results/figures/11_map_parallel_wind_cost_northward.png`
  - `results/figures/11_map_crosswind_cost_northward.png`
  - `results/figures/11_map_distance_cost.png`
  - `results/figures/11_map_food_cost.png`

## Quick-look figures

![Raw component histograms](../figures/11_raw_component_histograms.png)

![Standardized component histograms](../figures/11_standardized_component_histograms.png)

![Wind vs crosswind standardized costs](../figures/11_wind_vs_crosswind_scatter.png)

![Parallel wind cost map](../figures/11_map_parallel_wind_cost_northward.png)

![Crosswind cost map](../figures/11_map_crosswind_cost_northward.png)

![Distance cost map](../figures/11_map_distance_cost.png)

![Food cost map](../figures/11_map_food_cost.png)

## Interpretation
This step now does what it should scientifically: it creates an explicit directional cost graph while keeping the food surface behavior consistent with the published logic that poor-food cells must be expensive.

The four maps are also useful because they separate two different views of the model:
- edge-level directional costs used in the real path calculations
- cell-level component surfaces used for intuitive inspection

For the wind maps, the northward-flight assumption is only for visualizing the directional wind components as a global surface. The real graph still uses each actual edge bearing.

## Points to watch
- the distance component now represents true H3 edge length, which is an intentional refinement relative to the legacy constant-per-step distance term
- the legacy constant distance reference extracted from the standardized wind term is **{legacy_ref:.3f}**, which provides a direct bridge back to the earlier formulation
- the visual wind maps are diagnostic surfaces, not replacements for the directional edge-level calculations

## Next step
Combine these standardized components using selected weight sets and run the first Dijkstra path calculation for the H3 graph.
'''
    REPORT_PATH.write_text(report)

    print("Computed H3 edge cost components")
    print(f"rows: {len(out)}")
    print(f"written to: {OUTPUT_PATH}")
    print(f"report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
