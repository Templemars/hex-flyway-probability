#!/usr/bin/env python3
"""
Interpret the top RMSE behaviors for a chosen benchmark case using saved route
and RMSE outputs only.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from flyway_h3.cases import build_case_map
from flyway_h3.workflow_utils import route_points_from_group


RESULTS_TABLE_DIR = PROJECT_ROOT / "results" / "tables"
RESULTS_FIGURE_DIR = PROJECT_ROOT / "results" / "figures"
RESULTS_REPORT_DIR = PROJECT_ROOT / "results" / "reports"
CASE_MAP = build_case_map(PROJECT_ROOT)


def main() -> None:
    case_key = sys.argv[1] if len(sys.argv) > 1 else "svalbard_spring"
    if case_key not in CASE_MAP:
        raise SystemExit(f"Unknown case '{case_key}'. Choose from: {', '.join(sorted(CASE_MAP))}")
    cfg = CASE_MAP[case_key]

    rmse_path = RESULTS_TABLE_DIR / f"{cfg['eval_prefix']}_rmse.csv"
    band_path = RESULTS_TABLE_DIR / f"{cfg['eval_prefix']}_route_band_summaries.csv"
    routes_path = RESULTS_TABLE_DIR / f"{cfg['route_prefix']}_paths.csv"
    benchmark_path = cfg["benchmark_path"]
    output_top20_path = RESULTS_TABLE_DIR / f"{cfg['interpret_prefix']}_rmse_behaviors.csv"
    output_band_error_path = RESULTS_TABLE_DIR / f"{cfg['interpret_prefix']}_band_error_summary.csv"
    figure_coeff_scatter = RESULTS_FIGURE_DIR / f"{cfg['interpret_prefix']}_coefficient_scatter.png"
    figure_band_error = RESULTS_FIGURE_DIR / f"{cfg['interpret_prefix']}_band_errors.png"
    figure_route_agreement = RESULTS_FIGURE_DIR / f"{cfg['interpret_prefix']}_route_agreement.png"
    report_path = RESULTS_REPORT_DIR / f"{cfg['interpret_prefix']}_rmse_behaviors.md"

    rmse_df = pd.read_csv(rmse_path)
    band_df = pd.read_csv(band_path)
    routes_df = pd.read_csv(routes_path)
    benchmark = pd.read_csv(benchmark_path)

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

    output_top20_path.parent.mkdir(parents=True, exist_ok=True)
    figure_coeff_scatter.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    top20.to_csv(output_top20_path, index=False)
    band_error_summary.to_csv(output_band_error_path, index=False)

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
    fig.savefig(figure_coeff_scatter, dpi=170)
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
    ax.set_title(f"Top 20 {cfg['title_label']} route errors by latitude band")
    ax.legend()
    fig.savefig(figure_band_error, dpi=170)
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
    ax.set_title(f"Agreement structure among top 20 {cfg['title_label']} RMSE routes")
    ax.legend()
    fig.savefig(figure_route_agreement, dpi=170)
    plt.close(fig)

    best = top20.iloc[0]
    coeff_text = "\n".join([f"- {row.coefficient}: min {row.min:.1f}, median {row.median:.1f}, max {row.max:.1f}" for row in coeff_summary.itertuples(index=False)])
    lowest_error_band = band_error_summary.sort_values("mean_abs_lon_error_km").iloc[0]
    highest_error_band = band_error_summary.sort_values("mean_abs_lon_error_km", ascending=False).iloc[0]

    report = f'''# Interpret top RMSE {cfg['title_label']} behaviors

## Question
What structure appears among the 20 lowest-RMSE H3 {cfg['title_label']} routes, and where do they still diverge most strongly from the benchmark flyway?

## Outputs
- top-20 RMSE table: `{output_top20_path.relative_to(PROJECT_ROOT)}`
- top-20 band-error summary: `{output_band_error_path.relative_to(PROJECT_ROOT)}`
- coefficient scatter figure: `{figure_coeff_scatter.relative_to(PROJECT_ROOT)}`
- latitude-band error figure: `{figure_band_error.relative_to(PROJECT_ROOT)}`
- route-agreement figure: `{figure_route_agreement.relative_to(PROJECT_ROOT)}`

## Quick-look figures

![Top 20 coefficient scatter](../figures/{figure_coeff_scatter.name})

![Top 20 band errors](../figures/{figure_band_error.name})

![Top 20 route agreement](../figures/{figure_route_agreement.name})

## Top-ranked behavior
- behavior: **{best['behavior']}**
- RMSE: **{best['rmse_km']:.1f} km**
- weights: **({best['a_wind']:.1f}, {best['b_crosswind']:.1f}, {best['c_distance']:.1f}, {best['d_food']:.1f})**

## Coefficient structure among top 20
{coeff_text}

## Latitude-band error structure
- lowest mean top-20 error band: **{lowest_error_band['lat_band']}**, mean absolute error **{lowest_error_band['mean_abs_lon_error_km']:.1f} km**
- highest mean top-20 error band: **{highest_error_band['lat_band']}**, mean absolute error **{highest_error_band['mean_abs_lon_error_km']:.1f} km**

## Efficiency note
This interpretation reuses the saved RMSE, band-summary, and route outputs only.
'''
    report_path.write_text(report)

    print(f"Interpreted top RMSE {case_key} behaviors")
    print(f"top behaviors analyzed: {len(top20)}")
    print(f"best behavior: {best['behavior']}")
    print(f"report: {report_path}")


if __name__ == "__main__":
    main()
