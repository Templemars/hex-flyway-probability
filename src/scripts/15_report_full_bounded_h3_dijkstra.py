#!/usr/bin/env python3
"""
Produce figures and report for the full bounded H3 Dijkstra sweep from saved outputs.

This script must not rerun the route simulation. It only reads saved results.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PATHS_PATH = PROJECT_ROOT / "results" / "tables" / "15_svalbard_full_bounded_dijkstra_paths.csv"
SUMMARY_PATH = PROJECT_ROOT / "results" / "tables" / "15_svalbard_full_bounded_dijkstra_summary.csv"
WEIGHTS_PATH = PROJECT_ROOT / "results" / "tables" / "15_svalbard_full_bounded_dijkstra_weight_sets.csv"
ENDPOINTS_PATH = PROJECT_ROOT / "results" / "tables" / "15_svalbard_full_bounded_dijkstra_endpoints.csv"
ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_environment_res3.csv"
FIGURE_PATH = PROJECT_ROOT / "results" / "figures" / "15_svalbard_full_bounded_dijkstra_routes.png"
FIGURE_DENSITY_PATH = PROJECT_ROOT / "results" / "figures" / "15_svalbard_full_bounded_dijkstra_routes_transparent.png"
FIGURE_HEATMAP_PATH = PROJECT_ROOT / "results" / "figures" / "15_svalbard_full_bounded_dijkstra_point_density_heatmap.png"
REPORT_PATH = PROJECT_ROOT / "results" / "reports" / "15_run-full-bounded-h3-dijkstra.md"


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
    ax.scatter(masked["lon"], masked["lat"], s=90, marker="h", color="#c8b08f", alpha=0.75, linewidths=0)
    ax.scatter(supported["lon"], supported["lat"], s=65, marker="h", color="#dceaf7", alpha=0.20, linewidths=0)
    for _, route in path_df.groupby("behavior"):
        lons = [route.iloc[0]["source_lon"]] + route["target_lon"].tolist()
        lats = [route.iloc[0]["source_lat"]] + route["target_lat"].tolist()
        ax.plot(lons, lats, color="#355f8d", linewidth=2.8, alpha=0.10)
    ax.scatter([start_record["lon"], end_record["lon"]], [start_record["lat"], end_record["lat"]], color="black", s=35, marker="x")
    ax.set_title("Full bounded H3 Dijkstra sweep, Svalbard spring")
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    fig.savefig(FIGURE_PATH, dpi=170)
    plt.close(fig)

    point_df = path_df[["source_lon", "source_lat"]].rename(columns={"source_lon": "lon", "source_lat": "lat"}).copy()
    end_points = path_df.groupby("behavior").tail(1)[["target_lon", "target_lat"]].rename(columns={"target_lon": "lon", "target_lat": "lat"})
    point_df = pd.concat([point_df, end_points], ignore_index=True)
    lon_bins = np.arange(-95, 36, 2.0)
    lat_bins = np.arange(-80, 86, 2.0)
    heatmap, xedges, yedges = np.histogram2d(point_df["lon"], point_df["lat"], bins=[lon_bins, lat_bins])
    heatmap = heatmap.T

    fig, ax = plt.subplots(figsize=(8.2, 10.5), constrained_layout=True)
    ax.scatter(masked["lon"], masked["lat"], s=90, marker="h", color="#c8b08f", alpha=0.5, linewidths=0)
    mesh = ax.pcolormesh(xedges, yedges, heatmap, cmap="magma", shading="auto")
    cbar = fig.colorbar(mesh, ax=ax)
    cbar.set_label("Route-point density per 2° bin")
    ax.set_title("Full bounded H3 Dijkstra sweep, Atlantic point-density heatmap")
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    fig.savefig(FIGURE_HEATMAP_PATH, dpi=170)
    plt.close(fig)

    report = f'''# Run full bounded H3 Dijkstra sweep

## Question
What do all coefficient combinations from the currently documented bounded H3 behavior grid produce for the Svalbard spring case?

## Important scope note
This sweep uses the currently documented bounded grid:
- `a` wind from 0.0 to 1.0 by 0.1
- `b` crosswind from 0.0 to 0.5 by 0.1
- `c` distance from 0.0 to 1.0 by 0.1
- `d` food from 0.0 to 0.5 by 0.1
- `a + b + c + d = 1.0`

Under those rules, the sweep contains **{len(weights_df)}** behaviors.
This is explicitly the full bounded grid under the current project rules, not a claim that it exactly reproduces the paper's 195-filtered behavior set.

## Endpoint rule used
- start point = first row of `gdf_SS_10.csv`
- end point = last row of `gdf_SS_10.csv`
- both matched to nearest H3 cells

See:
- `results/tables/15_svalbard_full_bounded_dijkstra_endpoints.csv`

## Outputs
- path table: `results/tables/15_svalbard_full_bounded_dijkstra_paths.csv`
- route summary table: `results/tables/15_svalbard_full_bounded_dijkstra_summary.csv`
- weight table: `results/tables/15_svalbard_full_bounded_dijkstra_weight_sets.csv`
- endpoint table: `results/tables/15_svalbard_full_bounded_dijkstra_endpoints.csv`
- route overview figure: `results/figures/15_svalbard_full_bounded_dijkstra_routes.png`
- route-point density heatmap: `results/figures/15_svalbard_full_bounded_dijkstra_point_density_heatmap.png`

## Quick-look figures

![Full bounded H3 Dijkstra sweep](../figures/15_svalbard_full_bounded_dijkstra_routes.png)

![Full bounded H3 Dijkstra sweep, Atlantic point-density heatmap](../figures/15_svalbard_full_bounded_dijkstra_point_density_heatmap.png)

## Run summary
- number of tested behaviors: **{len(weights_df)}**
- number of successful route runs: **{len(summary_df)}**

## Interpretation
This step creates the full candidate pool under the currently documented bounded coefficient rules. The main goal is not to identify the route with the lowest internal modeled path cost, but to generate the full set of candidate least-cost paths that can later be compared against the Svalbard spring benchmark flyway.

The wide semi-transparent line figures are meant to show overlap density directly. Where many routes reuse the same corridor, opacity builds up. The Atlantic point-density heatmap provides a second view of the same structure using route-point counts per 2° bin.

The key things to inspect visually are:
- whether the route family collapses into a few dominant corridors or fills a broad envelope
- whether some combinations appear to produce visibly implausible detours or extreme spread
- whether the route cloud suggests that the current graph and endpoint setup are capable of spanning the benchmark flyway geometry at all
- whether the semi-transparent wide-line plots and the point-density heatmap reveal concentrated corridor use or a much more diffuse route field across the Atlantic domain

## Efficiency note
This report script reuses saved simulation outputs and does not rerun the costly Dijkstra sweep.

## Next step
Use this full bounded route set as the candidate pool for the first explicit route-to-benchmark comparison against the Svalbard spring 10-degree mean flyway.
'''
    REPORT_PATH.write_text(report)

    print("Rendered full bounded H3 Dijkstra report from saved outputs")
    print(f"tested behaviors: {len(weights_df)}")
    print(f"successful routes: {len(summary_df)}")
    print(f"report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
