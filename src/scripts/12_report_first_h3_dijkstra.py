#!/usr/bin/env python3
"""
Render figures and report for the Svalbard spring first H3 Dijkstra prototype
from saved step-12 outputs only.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PATHS_PATH = PROJECT_ROOT / "data" / "processed" / "routes" / "h3_dijkstra_svalbard_spring_paths.csv"
SUMMARY_PATH = PROJECT_ROOT / "results" / "tables" / "12_svalbard_dijkstra_summary.csv"
WEIGHTS_PATH = PROJECT_ROOT / "results" / "tables" / "12_svalbard_dijkstra_weight_sets.csv"
ENDPOINTS_PATH = PROJECT_ROOT / "results" / "tables" / "12_svalbard_dijkstra_endpoints.csv"
FAILURES_PATH = PROJECT_ROOT / "results" / "tables" / "12_svalbard_dijkstra_failures.csv"
ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_environment_res3.csv"
FIGURE_PATH = PROJECT_ROOT / "results" / "figures" / "12_svalbard_dijkstra_routes.png"
OVERLAY_FIGURE_PATH = PROJECT_ROOT / "results" / "figures" / "12_component_maps_with_lcps.png"
REPORT_PATH = PROJECT_ROOT / "results" / "reports" / "12_run-first-h3-dijkstra.md"


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
    failed_df = pd.read_csv(FAILURES_PATH) if FAILURES_PATH.exists() else pd.DataFrame()
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
    ax.set_title("First H3 Dijkstra prototype routes, Svalbard spring")
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    if successful_behaviors:
        ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8)
    fig.savefig(FIGURE_PATH, dpi=170)
    plt.close(fig)

    background_cols = {
        "support_only": ("w_cost", "Support cost background with support-only LCP"),
        "crosswind_only": ("c_cost", "Crosswind cost background with crosswind-only LCP"),
        "distance_only": ("d_cost", "Distance cost background with distance-only LCP"),
        "food_only": ("f_cost", "Food cost background with food-only LCP"),
    }
    map_env = env.loc[env["has_wind_support"], ["h3_cell", "lon", "lat", "u10", "v10", "chlor_a"]].copy()
    northward_support = map_env["v10"]
    pos_floor = map_env.loc[map_env["chlor_a"] > 0, "chlor_a"].min()
    map_env["w_cost"] = 100.0 * np.abs(northward_support - np.nanpercentile(northward_support.to_numpy(), 99)) / np.nanpercentile(np.abs(northward_support - np.nanpercentile(northward_support.to_numpy(), 99)), 99)
    map_env["c_cost"] = 100.0 * np.abs(map_env["u10"]) / np.nanpercentile(np.abs(map_env["u10"]).to_numpy(), 99)
    northward_distance_lookup = path_df.groupby("source_h3", as_index=False)["d_cost"].first()
    map_env = map_env.merge(northward_distance_lookup, left_on="h3_cell", right_on="source_h3", how="left")
    map_env["f_cost"] = 100.0 * np.abs(np.where(np.log(map_env["chlor_a"].clip(lower=pos_floor)) <= -1, np.log(map_env["chlor_a"].clip(lower=pos_floor)), -1) + 1) / np.nanpercentile(np.abs(np.where(np.log(map_env["chlor_a"].clip(lower=pos_floor)) <= -1, np.log(map_env["chlor_a"].clip(lower=pos_floor)), -1) + 1), 99)
    shared_overlay_max = float(np.nanpercentile(map_env[["w_cost", "c_cost", "d_cost", "f_cost"]].to_numpy(), 99))

    fig, axes = plt.subplots(2, 2, figsize=(11, 13), constrained_layout=True)
    for ax, behavior in zip(axes.ravel(), ["support_only", "crosswind_only", "distance_only", "food_only"]):
        value_col, title = background_cols[behavior]
        sc = draw_component_map_panel(ax, map_env, value_col, masked, title, 0.0, shared_overlay_max)
        route = path_df[path_df["behavior"] == behavior]
        if not route.empty:
            lons = [route.iloc[0]["source_lon"]] + route["target_lon"].tolist()
            lats = [route.iloc[0]["source_lat"]] + route["target_lat"].tolist()
            ax.plot(lons, lats, color="crimson", linewidth=2.0)
        cbar = fig.colorbar(sc, ax=ax)
        cbar.set_label(f"Standardized cost (SCU), shared scale 0 to {shared_overlay_max:.1f}")
    fig.savefig(OVERLAY_FIGURE_PATH, dpi=170)
    plt.close(fig)

    best = summary_df.iloc[0] if not summary_df.empty else None
    report = f'''# Run first H3 Dijkstra prototype

## Question
What happens when the first Svalbard spring H3 Dijkstra tests are run under four extreme single-factor behaviors, using the current prototype endpoint rule and the ERA5-supported routing mask?

## Outputs
- path table: `data/processed/routes/h3_dijkstra_svalbard_spring_paths.csv`
- route summary table: `results/tables/12_svalbard_dijkstra_summary.csv`
- weight table: `results/tables/12_svalbard_dijkstra_weight_sets.csv`
- endpoint table: `results/tables/12_svalbard_dijkstra_endpoints.csv`
- route figure: `results/figures/12_svalbard_dijkstra_routes.png`
- diagnostic overlay figure: `results/figures/12_component_maps_with_lcps.png`

## Quick-look figure

![First H3 Dijkstra prototype routes](../figures/12_svalbard_dijkstra_routes.png)

![Diagnostic component maps with corresponding least-cost paths](../figures/12_component_maps_with_lcps.png)

## Run status summary
- number of tested behaviors: **{len(weights_df)}**
- number of successful route runs: **{0 if summary_df.empty else len(summary_df)}**
- number of failed route runs: **{0 if failed_df.empty else len(failed_df)}**

## Efficiency note
This reporting step reuses saved step-12 route outputs and does not rerun Dijkstra.
'''
    if best is not None:
        report += f"\nAdditional route summary:\n- lowest total modeled path cost in this prototype batch: **{best['behavior']}**\n- corresponding total cost: **{best['total_cost']:.3f}**\n- corresponding total distance: **{best['total_distance_km']:.1f} km**\n"
    REPORT_PATH.write_text(report)
    print("Rendered Svalbard step-12 report from saved outputs")


if __name__ == "__main__":
    main()
