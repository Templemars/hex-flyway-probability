#!/usr/bin/env python3
"""
Evaluate the saved full bounded Svalbard H3 route sweep against the benchmark
10-degree mean flyway using RMSE on median longitude by latitude band.

This script reads saved route outputs only. It does not rerun simulations.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PATHS_PATH = PROJECT_ROOT / "results" / "tables" / "15_svalbard_full_bounded_dijkstra_paths.csv"
WEIGHTS_PATH = PROJECT_ROOT / "results" / "tables" / "15_svalbard_full_bounded_dijkstra_weight_sets.csv"
BENCHMARK_PATH = PROJECT_ROOT / "data" / "raw" / "benchmark_from_2025" / "gdf_SS_10.csv"
ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_environment_res3.csv"
OUTPUT_RMSE_PATH = PROJECT_ROOT / "results" / "tables" / "16_svalbard_full_bounded_rmse.csv"
OUTPUT_BAND_PATH = PROJECT_ROOT / "results" / "tables" / "16_svalbard_full_bounded_route_band_summaries.csv"
FIGURE_TOP_PATH = PROJECT_ROOT / "results" / "figures" / "16_svalbard_top_rmse_routes.png"
FIGURE_COEFF_PATH = PROJECT_ROOT / "results" / "figures" / "16_svalbard_top_rmse_coefficient_boxplots.png"
REPORT_PATH = PROJECT_ROOT / "results" / "reports" / "16_evaluate-full-bounded-rmse.md"


def assign_lat_band(lat: pd.Series) -> pd.Series:
    edges = np.arange(-80, 71, 10)
    labels = [f"({lo}, {hi}]" for lo, hi in zip(edges[:-1], edges[1:])]
    return pd.cut(lat, bins=edges, labels=labels, include_lowest=False, right=True)


def route_points_from_group(route: pd.DataFrame) -> pd.DataFrame:
    points = pd.DataFrame(
        {
            "lon": [route.iloc[0]["source_lon"]] + route["target_lon"].tolist(),
            "lat": [route.iloc[0]["source_lat"]] + route["target_lat"].tolist(),
        }
    )
    return points


def main() -> None:
    path_df = pd.read_csv(PATHS_PATH)
    weights_df = pd.read_csv(WEIGHTS_PATH)
    benchmark = pd.read_csv(BENCHMARK_PATH)
    env = pd.read_csv(ENV_PATH)

    benchmark = benchmark[["lat_bins_10", "lat_median10", "lon_median10"]].copy()
    benchmark = benchmark.rename(columns={"lat_bins_10": "lat_band", "lat_median10": "benchmark_lat_median", "lon_median10": "benchmark_lon_median"})

    band_rows = []
    rmse_rows = []
    route_lines = {}

    for behavior, route in path_df.groupby("behavior"):
        points = route_points_from_group(route)
        points["lat_band"] = assign_lat_band(points["lat"])
        route_summary = (
            points.dropna(subset=["lat_band"])
            .groupby("lat_band")
            .agg(route_lat_median=("lat", "median"), route_lon_median=("lon", "median"), n_points=("lon", "size"))
            .reset_index()
        )
        merged = benchmark.merge(route_summary, on="lat_band", how="left")
        merged["behavior"] = behavior
        merged["squared_lon_error"] = (merged["route_lon_median"] - merged["benchmark_lon_median"]) ** 2
        valid = merged.dropna(subset=["route_lon_median", "benchmark_lon_median"])
        if valid.empty:
            rmse = np.nan
            n_bands = 0
        else:
            rmse = float(np.sqrt(valid["squared_lon_error"].mean()))
            n_bands = int(len(valid))
        band_rows.extend(merged.to_dict(orient="records"))
        rmse_rows.append({"behavior": behavior, "rmse_lon_deg": rmse, "n_compared_bands": n_bands})
        route_lines[behavior] = points

    band_df = pd.DataFrame(band_rows)
    rmse_df = pd.DataFrame(rmse_rows).merge(weights_df, on="behavior", how="left").sort_values(["rmse_lon_deg", "behavior"])

    OUTPUT_RMSE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIGURE_TOP_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    rmse_df.to_csv(OUTPUT_RMSE_PATH, index=False)
    band_df.to_csv(OUTPUT_BAND_PATH, index=False)

    top = rmse_df.head(12).copy()
    env["has_wind_support"] = ~(env[["u10", "v10"]].isna().all(axis=1))
    masked = env.loc[~env["has_wind_support"]].copy()
    supported = env.loc[env["has_wind_support"]].copy()

    fig, ax = plt.subplots(figsize=(8.2, 10.5), constrained_layout=True)
    ax.scatter(masked["lon"], masked["lat"], s=90, marker="h", color="#c8b08f", alpha=0.75, linewidths=0)
    ax.scatter(supported["lon"], supported["lat"], s=65, marker="h", color="#dceaf7", alpha=0.18, linewidths=0)
    ax.plot(benchmark["benchmark_lon_median"], benchmark["benchmark_lat_median"], color="black", linewidth=2.6, label="Benchmark 10° mean")
    colors = plt.cm.viridis(np.linspace(0.15, 0.95, max(len(top), 1)))
    for color, row in zip(colors, top.itertuples(index=False)):
        points = route_lines[row.behavior]
        ax.plot(points["lon"], points["lat"], color=color, linewidth=1.3, alpha=0.85, label=f"{row.behavior} RMSE={row.rmse_lon_deg:.2f}")
    ax.set_title("Top RMSE routes versus Svalbard spring benchmark")
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=7)
    fig.savefig(FIGURE_TOP_PATH, dpi=170)
    plt.close(fig)

    top20 = rmse_df.head(20).copy()
    coeff_data = [top20["a_wind"], top20["b_crosswind"], top20["c_distance"], top20["d_food"]]
    fig, ax = plt.subplots(figsize=(7.6, 6.8), constrained_layout=True)
    box = ax.boxplot(coeff_data, patch_artist=True, labels=["a_wind", "b_crosswind", "c_distance", "d_food"])
    colors = ["#4c78a8", "#72b7b2", "#f58518", "#54a24b"]
    for patch, color in zip(box["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    ax.set_title("Coefficient distributions among top 20 lowest-RMSE behaviors")
    ax.set_ylabel("Coefficient value")
    ax.set_ylim(0, 1)
    fig.savefig(FIGURE_COEFF_PATH, dpi=170)
    plt.close(fig)

    best = rmse_df.iloc[0]
    report = f'''# Evaluate full bounded Svalbard sweep by RMSE

## Question
Which behaviors from the saved 216-route full bounded Svalbard sweep best recreate the benchmark spring flyway summary in `gdf_SS_10.csv`?

## Evaluation rule
For each simulated route:
- reconstruct the route as an ordered polyline from saved route coordinates
- summarize the route by 10° latitude bands
- compute the median longitude of the simulated route within each band
- compare that to the benchmark median longitude in the same band
- compute RMSE across all bands where both benchmark and simulated values are available

This matches the benchmark-comparison logic much more closely than ranking by internal path cost.

## Inputs
- saved routes: `results/tables/15_svalbard_full_bounded_dijkstra_paths.csv`
- saved behavior table: `results/tables/15_svalbard_full_bounded_dijkstra_weight_sets.csv`
- benchmark summary: `data/raw/benchmark_from_2025/gdf_SS_10.csv`

## Outputs
- RMSE table: `results/tables/16_svalbard_full_bounded_rmse.csv`
- per-band route summaries: `results/tables/16_svalbard_full_bounded_route_band_summaries.csv`
- top-route map: `results/figures/16_svalbard_top_rmse_routes.png`
- coefficient boxplots for top 20 RMSE behaviors: `results/figures/16_svalbard_top_rmse_coefficient_boxplots.png`

## Quick-look figures

![Top RMSE routes versus benchmark](../figures/16_svalbard_top_rmse_routes.png)

![Coefficient boxplots among top 20 RMSE behaviors](../figures/16_svalbard_top_rmse_coefficient_boxplots.png)

## Main result
- lowest-RMSE behavior: **{best['behavior']}**
- lowest RMSE: **{best['rmse_lon_deg']:.3f} longitude degrees**
- compared latitude bands: **{int(best['n_compared_bands'])}**
- weights: **({best['a_wind']:.1f}, {best['b_crosswind']:.1f}, {best['c_distance']:.1f}, {best['d_food']:.1f})**

## Interpretation
This is the first ranking step that directly addresses the real scientific goal of the Svalbard spring prototype: which simulated least-cost paths best recreate the observed 10-degree mean flyway.

That makes this step much more meaningful than any earlier ranking by internal path cost. The RMSE table now provides the correct candidate ordering for further inspection.

The most important things to inspect next are:
- whether the lowest-RMSE behaviors cluster in a recognizable region of coefficient space
- whether the coefficient boxplots show clear concentration or broad spread for wind, crosswind, distance, and food among the top 20 behaviors
- whether the top routes converge on a coherent flyway shape or remain quite different despite similar RMSE values
- whether the top-ranked routes also look biologically reasonable when plotted, rather than only numerically favorable under the benchmark summary metric

## Efficiency note
This evaluation script reuses the saved full-sweep route outputs and does not rerun the Dijkstra simulations.

## Next step
Inspect the top RMSE behaviors in detail and decide whether to refine the coefficient space, compare against the paper's filtered behavior set, or move to the Netherlands spring case.
'''
    REPORT_PATH.write_text(report)

    print("Evaluated full bounded Svalbard sweep by RMSE")
    print(f"behaviors ranked: {len(rmse_df)}")
    print(f"best behavior: {best['behavior']}")
    print(f"best RMSE: {best['rmse_lon_deg']:.3f}")
    print(f"report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
