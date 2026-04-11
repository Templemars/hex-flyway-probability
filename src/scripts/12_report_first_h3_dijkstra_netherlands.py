#!/usr/bin/env python3
"""
Render figures and report for the Netherlands spring first H3 Dijkstra prototype
from saved step-12 outputs only.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PATHS_PATH = PROJECT_ROOT / "data" / "processed" / "routes" / "h3_dijkstra_netherlands_spring_paths.csv"
SUMMARY_PATH = PROJECT_ROOT / "results" / "tables" / "12_netherlands_dijkstra_summary.csv"
WEIGHTS_PATH = PROJECT_ROOT / "results" / "tables" / "12_netherlands_dijkstra_weight_sets.csv"
ENDPOINTS_PATH = PROJECT_ROOT / "results" / "tables" / "12_netherlands_dijkstra_endpoints.csv"
ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_environment_res3.csv"
FIGURE_PATH = PROJECT_ROOT / "results" / "figures" / "12_netherlands_dijkstra_routes.png"
OVERLAY_FIGURE_PATH = PROJECT_ROOT / "results" / "figures" / "12_netherlands_component_maps_with_lcps.png"
REPORT_PATH = PROJECT_ROOT / "results" / "reports" / "12_run-first-h3-dijkstra-netherlands.md"


def draw_component_map_panel(ax, df, value_col, masked_df, title, vmin, vmax):
    ax.scatter(masked_df["lon"], masked_df["lat"], s=75, marker="h", color="#c8b08f", alpha=0.55, linewidths=0)
    sc = ax.scatter(df["lon"], df["lat"], c=df[value_col], s=65, marker="h", cmap="viridis", linewidths=0, alpha=0.9, vmin=vmin, vmax=vmax)
    ax.set_title(title)
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    return sc


def main() -> None:
    path_df = pd.read_csv(PATHS_PATH)
    summary_df = pd.read_csv(SUMMARY_PATH)
    weights_df = pd.read_csv(WEIGHTS_PATH)
    endpoints_df = pd.read_csv(ENDPOINTS_PATH)
    env = pd.read_csv(ENV_PATH)

    env["has_wind_support"] = ~(env[["u10", "v10"]].isna().all(axis=1))
    masked = env.loc[~env["has_wind_support"]].copy()
    supported = env.loc[env["has_wind_support"]].copy()
    start_record = endpoints_df.loc[endpoints_df["endpoint_role"] == "start"].iloc[0]
    end_record = endpoints_df.loc[endpoints_df["endpoint_role"] == "end"].iloc[0]

    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8.2, 10.5), constrained_layout=True)
    ax.scatter(masked["lon"], masked["lat"], s=90, marker="h", color="#c8b08f", alpha=0.75, linewidths=0, label="Outside ERA5-supported mask")
    ax.scatter(supported["lon"], supported["lat"], s=65, marker="h", color="#dceaf7", alpha=0.45, linewidths=0, label="ERA5-supported domain")
    successful_behaviors = list(summary_df["behavior"]) if not summary_df.empty else []
    colors = plt.cm.tab10(np.linspace(0, 1, max(len(successful_behaviors), 1)))
    for color, behavior in zip(colors, successful_behaviors):
        route = path_df[path_df["behavior"] == behavior]
        if route.empty:
            continue
        lons = [route.iloc[0]["source_lon"]] + route["target_lon"].tolist()
        lats = [route.iloc[0]["source_lat"]] + route["target_lat"].tolist()
        ax.plot(lons, lats, color=color, linewidth=1.8, label=behavior)
    ax.scatter([start_record["lon"], end_record["lon"]], [start_record["lat"], end_record["lat"]], color="black", s=40, marker="x")
    ax.set_title("First H3 Dijkstra prototype routes, Netherlands spring")
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    if successful_behaviors:
        ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8)
    fig.savefig(FIGURE_PATH, dpi=170)
    plt.close(fig)

    map_env = env.loc[env["has_wind_support"], ["h3_cell", "lon", "lat", "u10", "v10", "chlor_a"]].copy()
    northward_support = map_env["v10"]
    crosswind = map_env["u10"].abs()
    food = np.log10(map_env["chlor_a"].clip(lower=map_env.loc[map_env["chlor_a"] > 0, "chlor_a"].min()))
    food = food.max() - food
    distance_constant = float(path_df["d_cost"].median())
    map_env["w_cost"] = northward_support.max() - northward_support
    map_env["c_cost"] = crosswind
    map_env["d_cost"] = distance_constant
    map_env["f_cost"] = food
    vmax = float(np.nanpercentile(np.concatenate([map_env[col].to_numpy() for col in ["w_cost", "c_cost", "d_cost", "f_cost"]]), 99))

    background_cols = {
        "support_only": ("w_cost", "Support cost background with support-only LCP"),
        "crosswind_only": ("c_cost", "Crosswind cost background with crosswind-only LCP"),
        "distance_only": ("d_cost", "Distance cost background with distance-only LCP"),
        "food_only": ("f_cost", "Food cost background with food-only LCP"),
    }

    fig, axes = plt.subplots(2, 2, figsize=(11.5, 12.0), constrained_layout=True)
    for ax, behavior in zip(axes.flatten(), ["support_only", "crosswind_only", "distance_only", "food_only"]):
        value_col, title = background_cols[behavior]
        sc = draw_component_map_panel(ax, map_env, value_col, masked, title, 0.0, vmax)
        route = path_df[path_df["behavior"] == behavior]
        if not route.empty:
            lons = [route.iloc[0]["source_lon"]] + route["target_lon"].tolist()
            lats = [route.iloc[0]["source_lat"]] + route["target_lat"].tolist()
            ax.plot(lons, lats, color="crimson", linewidth=2.2)
            ax.scatter([start_record["lon"], end_record["lon"]], [start_record["lat"], end_record["lat"]], color="black", s=28, marker="x")
        cbar = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label("Standardized cost units")
    fig.savefig(OVERLAY_FIGURE_PATH, dpi=170)
    plt.close(fig)

    report = f'''# Run first H3 Dijkstra prototype, Netherlands spring

## Question
What do the four extreme single-factor prototype behaviors produce for the Netherlands spring case on the H3 cost graph?

## Endpoint rule used
- start point = first row of `gdf_NS_10.csv`
- end point = last row of `gdf_NS_10.csv`
- both matched to nearest H3 cells

## Outputs
- path table: `data/processed/routes/h3_dijkstra_netherlands_spring_paths.csv`
- route summary table: `results/tables/12_netherlands_dijkstra_summary.csv`
- weight table: `results/tables/12_netherlands_dijkstra_weight_sets.csv`
- endpoint table: `results/tables/12_netherlands_dijkstra_endpoints.csv`
- route overview figure: `results/figures/12_netherlands_dijkstra_routes.png`
- component-overlay figure: `results/figures/12_netherlands_component_maps_with_lcps.png`

## Quick-look figures

![First Netherlands H3 Dijkstra routes](../figures/12_netherlands_dijkstra_routes.png)

![Netherlands component maps with LCPs](../figures/12_netherlands_component_maps_with_lcps.png)

## Run summary
- number of tested behaviors: **{len(weights_df)}**
- number of successful route runs: **{0 if summary_df.empty else len(summary_df)}**

## Efficiency note
This reporting step reuses saved step-12 route outputs and does not rerun Dijkstra.
'''
    REPORT_PATH.write_text(report)

    print("Rendered Netherlands step-12 report from saved outputs")
    print(f"report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
