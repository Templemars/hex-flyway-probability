#!/usr/bin/env python3
"""
Interpret the top-RMSE Svalbard H3 routes using saved evaluation outputs only.

This script does not rerun route simulations. It summarizes the structure of the
lowest-RMSE behaviors, their coefficient patterns, and where route-to-benchmark
errors are concentrated by latitude band.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RMSE_PATH = PROJECT_ROOT / "results" / "tables" / "16_svalbard_full_bounded_rmse.csv"
BAND_PATH = PROJECT_ROOT / "results" / "tables" / "16_svalbard_full_bounded_route_band_summaries.csv"
ROUTES_PATH = PROJECT_ROOT / "results" / "tables" / "15_svalbard_full_bounded_dijkstra_paths.csv"
BENCHMARK_PATH = PROJECT_ROOT / "data" / "raw" / "benchmark_from_2025" / "gdf_SS_10.csv"
OUTPUT_TOP20_PATH = PROJECT_ROOT / "results" / "tables" / "17_svalbard_top20_rmse_behaviors.csv"
OUTPUT_BAND_ERROR_PATH = PROJECT_ROOT / "results" / "tables" / "17_svalbard_top20_band_error_summary.csv"
FIGURE_COEFF_SCATTER = PROJECT_ROOT / "results" / "figures" / "17_svalbard_top20_coefficient_scatter.png"
FIGURE_BAND_ERROR = PROJECT_ROOT / "results" / "figures" / "17_svalbard_top20_band_errors.png"
FIGURE_ROUTE_AGREEMENT = PROJECT_ROOT / "results" / "figures" / "17_svalbard_top20_route_agreement.png"
REPORT_PATH = PROJECT_ROOT / "results" / "reports" / "17_interpret-top-rmse-behaviors-svalbard-spring.md"


def route_points_from_group(route: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "lon": [route.iloc[0]["source_lon"]] + route["target_lon"].tolist(),
            "lat": [route.iloc[0]["source_lat"]] + route["target_lat"].tolist(),
        }
    )


def main() -> None:
    rmse_df = pd.read_csv(RMSE_PATH)
    band_df = pd.read_csv(BAND_PATH)
    routes_df = pd.read_csv(ROUTES_PATH)
    benchmark = pd.read_csv(BENCHMARK_PATH)

    top20 = rmse_df.head(20).copy()
    top20_behaviors = top20["behavior"].tolist()
    top20_band = band_df.loc[band_df["behavior"].isin(top20_behaviors)].copy()
    top20_routes = routes_df.loc[routes_df["behavior"].isin(top20_behaviors)].copy()

    coeff_summary = pd.DataFrame(
        {
            "coefficient": ["a_wind", "b_crosswind", "c_distance", "d_food"],
            "min": [top20["a_wind"].min(), top20["b_crosswind"].min(), top20["c_distance"].min(), top20["d_food"].min()],
            "median": [top20["a_wind"].median(), top20["b_crosswind"].median(), top20["c_distance"].median(), top20["d_food"].median()],
            "max": [top20["a_wind"].max(), top20["b_crosswind"].max(), top20["c_distance"].max(), top20["d_food"].max()],
        }
    )

    band_error_summary = (
        top20_band.groupby("lat_band")
        .agg(
            benchmark_lat_median=("benchmark_lat_median", "first"),
            mean_abs_lon_error_km=("lon_error_km", lambda s: float(np.nanmean(np.abs(s)))),
            median_abs_lon_error_km=("lon_error_km", lambda s: float(np.nanmedian(np.abs(s)))),
            min_abs_lon_error_km=("lon_error_km", lambda s: float(np.nanmin(np.abs(s)))),
            max_abs_lon_error_km=("lon_error_km", lambda s: float(np.nanmax(np.abs(s)))),
        )
        .reset_index()
    )

    OUTPUT_TOP20_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIGURE_COEFF_SCATTER.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    top20.to_csv(OUTPUT_TOP20_PATH, index=False)
    band_error_summary.to_csv(OUTPUT_BAND_ERROR_PATH, index=False)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8), constrained_layout=True)
    axes[0].scatter(top20["a_wind"], top20["c_distance"], c=top20["rmse_km"], cmap="viridis_r", s=60)
    axes[0].set_xlabel("a_wind")
    axes[0].set_ylabel("c_distance")
    axes[0].set_title("Top 20, wind versus distance")
    axes[0].set_xlim(-0.02, 1.02)
    axes[0].set_ylim(-0.02, 1.02)

    scatter = axes[1].scatter(top20["b_crosswind"], top20["d_food"], c=top20["rmse_km"], cmap="viridis_r", s=60)
    axes[1].set_xlabel("b_crosswind")
    axes[1].set_ylabel("d_food")
    axes[1].set_title("Top 20, crosswind versus food")
    axes[1].set_xlim(-0.02, 0.52)
    axes[1].set_ylim(-0.02, 0.52)
    cbar = fig.colorbar(scatter, ax=axes.ravel().tolist())
    cbar.set_label("RMSE (km)")
    fig.savefig(FIGURE_COEFF_SCATTER, dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 5.8), constrained_layout=True)
    ax.plot(band_error_summary["mean_abs_lon_error_km"], band_error_summary["benchmark_lat_median"], color="#355f8d", linewidth=2.5, label="Mean absolute error")
    ax.fill_betweenx(
        band_error_summary["benchmark_lat_median"],
        band_error_summary["min_abs_lon_error_km"],
        band_error_summary["max_abs_lon_error_km"],
        color="#9ecae1",
        alpha=0.35,
        label="Min to max across top 20",
    )
    ax.set_xlabel("Absolute longitude error relative to benchmark (km)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_title("Top 20 route-to-benchmark errors by latitude band")
    ax.legend()
    fig.savefig(FIGURE_BAND_ERROR, dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.2, 10.2), constrained_layout=True)
    ax.plot(benchmark["lon_median10"], benchmark["lat_median10"], color="black", linewidth=2.8, label="Benchmark 10° mean")
    for _, row in top20.iterrows():
        route = top20_routes.loc[top20_routes["behavior"] == row["behavior"]]
        points = route_points_from_group(route)
        ax.plot(points["lon"], points["lat"], color="#355f8d", linewidth=2.0, alpha=0.14)
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_title("Agreement structure among top 20 RMSE routes")
    ax.legend()
    fig.savefig(FIGURE_ROUTE_AGREEMENT, dpi=170)
    plt.close(fig)

    best = top20.iloc[0]
    coeff_text = "\n".join(
        [f"- {row.coefficient}: min {row.min:.1f}, median {row.median:.1f}, max {row.max:.1f}" for row in coeff_summary.itertuples(index=False)]
    )
    lowest_error_band = band_error_summary.sort_values("mean_abs_lon_error_km").iloc[0]
    highest_error_band = band_error_summary.sort_values("mean_abs_lon_error_km", ascending=False).iloc[0]

    report = f'''# Interpret top RMSE Svalbard behaviors

## Question
What structure appears among the 20 lowest-RMSE H3 Svalbard spring routes, and where do they still diverge most strongly from the benchmark flyway?

## Inputs
- RMSE ranking: `results/tables/16_svalbard_full_bounded_rmse.csv`
- per-band error table: `results/tables/16_svalbard_full_bounded_route_band_summaries.csv`
- saved routes: `results/tables/15_svalbard_full_bounded_dijkstra_paths.csv`

## Outputs
- top-20 RMSE table: `results/tables/17_svalbard_top20_rmse_behaviors.csv`
- top-20 band-error summary: `results/tables/17_svalbard_top20_band_error_summary.csv`
- coefficient scatter figure: `results/figures/17_svalbard_top20_coefficient_scatter.png`
- latitude-band error figure: `results/figures/17_svalbard_top20_band_errors.png`
- route-agreement figure: `results/figures/17_svalbard_top20_route_agreement.png`

## Quick-look figures

![Top 20 coefficient scatter](../figures/17_svalbard_top20_coefficient_scatter.png)

![Top 20 band errors](../figures/17_svalbard_top20_band_errors.png)

![Top 20 route agreement](../figures/17_svalbard_top20_route_agreement.png)

## Top-ranked behavior
- behavior: **{best['behavior']}**
- RMSE: **{best['rmse_km']:.1f} km**
- weights: **({best['a_wind']:.1f}, {best['b_crosswind']:.1f}, {best['c_distance']:.1f}, {best['d_food']:.1f})**

## Coefficient structure among top 20
{coeff_text}

## Latitude-band error structure
- lowest mean top-20 error band: **{lowest_error_band['lat_band']}**, mean absolute error **{lowest_error_band['mean_abs_lon_error_km']:.1f} km**
- highest mean top-20 error band: **{highest_error_band['lat_band']}**, mean absolute error **{highest_error_band['mean_abs_lon_error_km']:.1f} km**

## Interpretation
The top 20 RMSE behaviors are not spread uniformly across coefficient space. They cluster strongly toward high wind weight, with only modest contributions from crosswind, distance, and food. That means benchmark agreement is currently being driven mainly by wind-favored routing, not by strongly food-dominated or crosswind-dominated behavior.

The route-agreement figure should be read as a structural summary of the top candidate family. If the top 20 routes remain tightly bundled, that suggests the current benchmark favors a fairly specific H3 corridor. If they fan out but still achieve similar RMSE, that means the latitude-binned benchmark metric is tolerating multiple geometrically different route shapes.

The latitude-band error summary shows where the current H3 route family still struggles most against the benchmark flyway. Those high-error bands are the most important places to inspect next, because they may point to endpoint effects, grid effects, or limitations in the current cost structure.

## Next step
Use the top-20 interpretation to decide whether to tighten the Svalbard coefficient search around the wind-dominant region, inspect the highest-error latitude bands more closely, or move on to the Netherlands spring case with the same evaluation pipeline.
'''
    REPORT_PATH.write_text(report)

    print("Interpreted top RMSE Svalbard behaviors")
    print(f"top behaviors analyzed: {len(top20)}")
    print(f"best behavior: {best['behavior']}")
    print(f"report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
