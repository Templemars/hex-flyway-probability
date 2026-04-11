#!/usr/bin/env python3
"""
Render figures and report for the Netherlands spring full bounded H3 sweep from
saved step-15 outputs only.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PATHS_PATH = PROJECT_ROOT / "results" / "tables" / "15_netherlands_full_bounded_dijkstra_paths.csv"
SUMMARY_PATH = PROJECT_ROOT / "results" / "tables" / "15_netherlands_full_bounded_dijkstra_summary.csv"
WEIGHTS_PATH = PROJECT_ROOT / "results" / "tables" / "15_netherlands_full_bounded_dijkstra_weight_sets.csv"
ENDPOINTS_PATH = PROJECT_ROOT / "results" / "tables" / "15_netherlands_full_bounded_dijkstra_endpoints.csv"
ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_environment_res3.csv"
FIGURE_PATH = PROJECT_ROOT / "results" / "figures" / "15_netherlands_full_bounded_dijkstra_routes.png"
FIGURE_HEATMAP_PATH = PROJECT_ROOT / "results" / "figures" / "15_netherlands_full_bounded_dijkstra_point_density_heatmap.png"
REPORT_PATH = PROJECT_ROOT / "results" / "reports" / "15_run-full-bounded-h3-dijkstra-netherlands.md"


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
    ax.set_title("Full bounded H3 Dijkstra sweep, Netherlands spring")
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
    positive_heat = heatmap[heatmap > 0]
    vmax = float(np.percentile(positive_heat, 99)) if positive_heat.size else 1.0

    fig, ax = plt.subplots(figsize=(8.2, 10.5), constrained_layout=True)
    ax.scatter(masked["lon"], masked["lat"], s=90, marker="h", color="#c8b08f", alpha=0.5, linewidths=0)
    mesh = ax.pcolormesh(xedges, yedges, heatmap, cmap="magma", shading="auto", vmin=0.0, vmax=vmax)
    cbar = fig.colorbar(mesh, ax=ax)
    cbar.set_label(f"Route-point density per 2° bin, capped at P99 = {vmax:.1f}")
    ax.set_title("Full bounded H3 Dijkstra sweep, Netherlands Atlantic point-density heatmap")
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    fig.savefig(FIGURE_HEATMAP_PATH, dpi=170)
    plt.close(fig)

    report = f'''# Run full bounded H3 Dijkstra sweep, Netherlands spring

## Question
What does the current full bounded H3 behavior grid produce for the Netherlands spring case?

## Outputs
- path table: `results/tables/15_netherlands_full_bounded_dijkstra_paths.csv`
- route summary table: `results/tables/15_netherlands_full_bounded_dijkstra_summary.csv`
- weight table: `results/tables/15_netherlands_full_bounded_dijkstra_weight_sets.csv`
- endpoint table: `results/tables/15_netherlands_full_bounded_dijkstra_endpoints.csv`
- route overview figure: `results/figures/15_netherlands_full_bounded_dijkstra_routes.png`
- route-point density heatmap: `results/figures/15_netherlands_full_bounded_dijkstra_point_density_heatmap.png`

## Quick-look figures

![Full bounded Netherlands routes](../figures/15_netherlands_full_bounded_dijkstra_routes.png)

![Full bounded Netherlands route density](../figures/15_netherlands_full_bounded_dijkstra_point_density_heatmap.png)

## Run summary
- number of tested behaviors: **{len(weights_df)}**
- number of successful route runs: **{0 if summary_df.empty else len(summary_df)}**

## Efficiency note
This reporting step reuses saved step-15 route outputs and does not rerun the full bounded sweep.
'''
    REPORT_PATH.write_text(report)

    print("Rendered Netherlands step-15 report from saved outputs")
    print(f"report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
