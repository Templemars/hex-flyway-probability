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
DIRECTIONAL_DISTANCE_PATH = PROJECT_ROOT / "results" / "tables" / "11_directional_edge_distance_summary.csv"
REPORT_PATH = PROJECT_ROOT / "results" / "reports" / "11_compute-h3-cost-components.md"
RAW_HIST_PATH = PROJECT_ROOT / "results" / "figures" / "11_raw_component_histograms.png"
STD_HIST_PATH = PROJECT_ROOT / "results" / "figures" / "11_standardized_component_histograms.png"
SCATTER_PATH = PROJECT_ROOT / "results" / "figures" / "11_wind_vs_crosswind_scatter.png"
DIRECTIONAL_DISTANCE_FIGURE_PATH = PROJECT_ROOT / "results" / "figures" / "11_directional_edge_distance_by_bearing.png"
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


def draw_component_map(
    df: pd.DataFrame,
    value_col: str,
    output_path: Path,
    title: str,
    colorbar_label: str,
    vmin: float,
    vmax: float,
    cmap: str = "viridis",
) -> None:
    fig, ax = plt.subplots(figsize=(11, 6.5), constrained_layout=True)
    plot_df = df.dropna(subset=[value_col]).copy()
    sc = ax.scatter(
        plot_df["lon"],
        plot_df["lat"],
        c=plot_df[value_col],
        s=10,
        cmap=cmap,
        linewidths=0,
        vmin=vmin,
        vmax=vmax,
    )
    ax.set_title(title)
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label(colorbar_label)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def select_northward_edge_distance(edge_df: pd.DataFrame) -> pd.Series:
    """For each source cell, choose the outgoing edge whose bearing is closest to north.

    This gives a real edge-distance quantity that is directionally aligned with the
    diagnostic northward maps for wind.
    """
    edges = edge_df[["source_h3", "edge_bearing_deg", "edge_distance_km"]].copy()
    circular_distance_to_north = np.abs(((edges["edge_bearing_deg"] + 180.0) % 360.0) - 180.0)
    edges["north_offset_deg"] = circular_distance_to_north
    edges = edges.sort_values(["source_h3", "north_offset_deg", "edge_distance_km"], ascending=[True, True, True])
    best_north = edges.drop_duplicates(subset=["source_h3"], keep="first")
    return pd.Series(best_north["edge_distance_km"].to_numpy(), index=best_north["source_h3"].to_numpy())


def summarize_directional_distance(edge_df: pd.DataFrame) -> pd.DataFrame:
    bearing_labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    sector = ((edge_df["edge_bearing_deg"] + 22.5) % 360 // 45).astype(int)
    out = edge_df[["edge_bearing_deg", "edge_distance_km", "source_lat"]].copy()
    out["bearing_sector"] = [bearing_labels[i] for i in sector]
    out["latitude_band"] = (np.floor(out["source_lat"] / 10) * 10).astype(int)

    summary = (
        out.groupby(["latitude_band", "bearing_sector"])["edge_distance_km"]
        .agg(["count", "mean", "median", "min", "max"])
        .reset_index()
        .sort_values(["latitude_band", "bearing_sector"])
    )
    return summary


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
    typical_edge_distance_km = percentile_50(df["edge_distance_km"])
    distance_cost_raw = (df["edge_distance_km"] - typical_edge_distance_km).clip(lower=0.0)
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

    directional_distance = summarize_directional_distance(out)
    directional_distance.to_csv(DIRECTIONAL_DISTANCE_PATH, index=False)

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

    fig, ax = plt.subplots(figsize=(10, 5.5), constrained_layout=True)
    for label, group in directional_distance.groupby("bearing_sector"):
        ax.plot(group["latitude_band"], group["mean"], marker="o", linewidth=1.5, label=label)
    ax.set_title("Mean edge distance by bearing sector and latitude band")
    ax.set_xlabel("Latitude band (degrees)")
    ax.set_ylabel("Mean edge distance (km)")
    ax.legend(title="Bearing sector", ncol=4, fontsize=8)
    fig.savefig(DIRECTIONAL_DISTANCE_FIGURE_PATH, dpi=160)
    plt.close(fig)

    # Component maps at cell level. For visualization, use the wind footprint as the support mask.
    northward_support = env["v10"]
    northward_parallel_raw = np.abs(northward_support - percentile_99(northward_support))
    northward_crosswind_raw = np.abs(env["u10"])
    env_map = env[["h3_cell", "lon", "lat", "u10", "v10", "chlor_a"]].copy()
    env_map["has_wind_support"] = ~(env_map[["u10", "v10"]].isna().all(axis=1))
    env_map["parallel_wind_cost_northward_raw"] = northward_parallel_raw
    env_map["crosswind_cost_northward_raw"] = northward_crosswind_raw
    northward_edge_distance = select_northward_edge_distance(out)
    env_map = env_map.merge(
        northward_edge_distance.rename("northward_edge_distance_km"),
        left_on="h3_cell",
        right_index=True,
        how="left",
    )
    env_map["food_cost_raw"] = compute_food_cost(env_map["chlor_a"])
    env_map["parallel_wind_cost_northward_std"] = standardize_to_100(env_map["parallel_wind_cost_northward_raw"])
    env_map["crosswind_cost_northward_std"] = standardize_to_100(env_map["crosswind_cost_northward_raw"])
    env_map["distance_cost_raw"] = (env_map["northward_edge_distance_km"] - typical_edge_distance_km).clip(lower=0.0)
    env_map["distance_cost_std"] = standardize_to_100(env_map["distance_cost_raw"].fillna(0.0))
    env_map["food_cost_std"] = standardize_to_100(env_map["food_cost_raw"])

    for col in [
        "parallel_wind_cost_northward_std",
        "crosswind_cost_northward_std",
        "distance_cost_std",
        "food_cost_std",
    ]:
        env_map.loc[~env_map["has_wind_support"], col] = np.nan

    map_max = float(
        np.nanpercentile(
            env_map[
                [
                    "parallel_wind_cost_northward_std",
                    "crosswind_cost_northward_std",
                    "distance_cost_std",
                    "food_cost_std",
                ]
            ].to_numpy(),
            99,
        )
    )

    draw_component_map(
        env_map,
        "parallel_wind_cost_northward_std",
        MAP_WIND_PATH,
        "Parallel wind cost surface for straight northward flight",
        f"Standardized cost (SCU), shared scale 0 to {map_max:.1f}",
        0.0,
        map_max,
    )
    draw_component_map(
        env_map,
        "crosswind_cost_northward_std",
        MAP_CROSSWIND_PATH,
        "Crosswind cost surface for straight northward flight",
        f"Standardized cost (SCU), shared scale 0 to {map_max:.1f}",
        0.0,
        map_max,
    )
    draw_component_map(
        env_map,
        "distance_cost_std",
        MAP_DISTANCE_PATH,
        "Distance cost surface from outgoing edge closest to north",
        f"Standardized cost (SCU), shared scale 0 to {map_max:.1f}",
        0.0,
        map_max,
    )
    draw_component_map(
        env_map,
        "food_cost_std",
        MAP_FOOD_PATH,
        "Food cost surface from chlorophyll-a",
        f"Standardized cost (SCU), shared scale 0 to {map_max:.1f}",
        0.0,
        map_max,
    )

    legacy_ref = out["legacy_constant_distance_reference"].iloc[0]
    zero_chla_count = int((env["chlor_a"] <= 0).sum())
    positive_floor = float(env.loc[env["chlor_a"] > 0, "chlor_a"].min()) if (env["chlor_a"] > 0).any() else 1e-6
    missing_support_count = int((~env_map["has_wind_support"]).sum())
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
- cells outside the common wind-supported map footprint: **{missing_support_count}**
- shared map color scale maximum (P99 cap across displayed map layers): **{map_max:.3f} SCU**

## Method
- compute directional edge costs for parallel wind, crosswind, extra edge distance relative to a typical neighbor step, and food
- standardize each component with the agreed P99-based scaling philosophy
- additionally produce four cell-level component maps for transparency
- for the two wind component maps, assume a bird flying in a straight northward direction everywhere
- for the distance map, assign to each cell the true distance of the outgoing edge whose bearing is closest to north
- for visualization only, use the wind-data footprint as a common support mask across all four maps so unsupported cells are not mistaken for valid low or high costs
- apply one shared color scale across all four maps, starting at 0 and ending at the shared P99 of the displayed standardized map values
- summarize edge distance by bearing sector and latitude band to check whether visible distance-map patterns reflect real directional anisotropy in the graph

## Key formulas used
- movement direction comes from the edge bearing for the edge-level table
- wind support is the projection of the source wind vector onto the movement direction
- raw parallel wind cost = distance from `P99(windsupport)`
- raw crosswind cost = magnitude of the wind component perpendicular to movement
- raw distance cost = extra H3 edge distance beyond the median H3 neighbor-step distance, floored at zero
- diagnostic distance map = extra distance of the outgoing edge whose bearing is closest to north, relative to the same median step length
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
  - `results/figures/11_directional_edge_distance_by_bearing.png`
  - `results/figures/11_map_parallel_wind_cost_northward.png`
  - `results/figures/11_map_crosswind_cost_northward.png`
  - `results/figures/11_map_distance_cost.png`
  - `results/figures/11_map_food_cost.png`

## Quick-look figures

![Raw component histograms](../figures/11_raw_component_histograms.png)

![Standardized component histograms](../figures/11_standardized_component_histograms.png)

![Wind vs crosswind standardized costs](../figures/11_wind_vs_crosswind_scatter.png)

![Directional edge distance by bearing](../figures/11_directional_edge_distance_by_bearing.png)

![Parallel wind cost map](../figures/11_map_parallel_wind_cost_northward.png)

![Crosswind cost map](../figures/11_map_crosswind_cost_northward.png)

![Distance cost map](../figures/11_map_distance_cost.png)

![Food cost map](../figures/11_map_food_cost.png)

## Interpretation
This step now does what it should scientifically: it creates an explicit directional cost graph while keeping the food surface behavior consistent with the published logic that poor-food cells must be expensive.

The main methodological refinement in this version is the distance term. The first H3 implementation used raw edge length scaled directly to the P99, which made most H3 edges cluster close to the upper standardized range because neighbor distances at one H3 resolution are fairly similar. The revised formulation is more defensible: it treats a typical median H3 neighbor step as the zero-baseline distance cost and penalizes only the extra distance beyond that baseline.

The four maps are also useful because they separate two different views of the model:
- edge-level directional costs used in the real path calculations
- cell-level component surfaces used for intuitive inspection

For the wind maps, the northward-flight assumption is only for visualizing the directional wind components as a global surface. The real graph still uses each actual edge bearing.
For the distance map, each cell is assigned the true distance of its outgoing edge closest to north. This is also diagnostic rather than part of the routing graph itself, but it is a real edge quantity rather than an artificial cumulative construction.

The pole issue in the earlier food map was not something I was happy with. It mixed genuinely poor-food cells with cells that simply lie outside the shared environmental support. Using the wind footprint as a visualization mask is the right fix for the maps, because it prevents unsupported cells from being visually interpreted as real food-cost values.

The directional distance diagnostic helps interpret the odd blue corridor patterns in the northward distance map. Those patterns are partly a consequence of selecting a single outgoing edge per cell for display, but the bearing-by-latitude summary lets us check whether there is also real directional variation in edge distances in the H3 graph.

## Points to watch
- the distance component in the routing model now represents extra H3 edge length relative to a typical median neighbor step, which is an intentional refinement relative to the legacy constant-per-step distance term
- the mapped northward distance surface is a separate diagnostic layer for interpretability, based on the extra length of a real outgoing northward edge per cell relative to the same baseline
- the common wind-footprint mask is a visualization choice for consistency and honesty across maps, not yet a modeling exclusion rule
- the shared P99-capped color scale makes map-to-map magnitude comparisons easier while preserving more contrast than a raw-maximum scale
- if the directional distance summary shows strong systematic bearing effects, we should keep that in mind when interpreting later Dijkstra behavior
- the median H3 neighbor-step baseline used for the revised distance term is **{typical_edge_distance_km:.3f} km**
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
