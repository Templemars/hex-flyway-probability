#!/usr/bin/env python3
"""
Evaluate a saved full bounded route sweep against its benchmark 10-degree mean
flyway summary using RMSE in km.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from flyway_h3.cases import build_case_map
from flyway_h3.workflow_utils import assign_lat_band, route_points_from_group


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_DIR = PROJECT_ROOT / "data" / "raw" / "benchmark_from_2025"
RESULTS_TABLE_DIR = PROJECT_ROOT / "results" / "tables"
RESULTS_FIGURE_DIR = PROJECT_ROOT / "results" / "figures"
RESULTS_REPORT_DIR = PROJECT_ROOT / "results" / "reports"
COEFFLIST_PATH = BENCHMARK_DIR / "coefflist.csv"
ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_environment_res3.csv"
CASE_MAP = build_case_map(PROJECT_ROOT)


def lon_degree_km_at_lat(lat_deg: pd.Series, delta_lon_deg: pd.Series) -> pd.Series:
    return 111.32 * np.cos(np.deg2rad(lat_deg)) * np.abs(delta_lon_deg)


def load_old_paper_coefficients() -> pd.DataFrame:
    raw = pd.read_csv(COEFFLIST_PATH)
    values = raw[raw.columns[-1]].to_numpy()
    coeffs = values.reshape(-1, 4)
    out = pd.DataFrame(coeffs, columns=["a_wind_oldR", "b_distance_oldR", "c_food_oldR", "d_crosswind_oldR"])
    out["a_wind"] = out["a_wind_oldR"]
    out["b_crosswind"] = out["d_crosswind_oldR"]
    out["c_distance"] = out["b_distance_oldR"]
    out["d_food"] = out["c_food_oldR"]
    return out[["a_wind", "b_crosswind", "c_distance", "d_food"]]


def main() -> None:
    case_key = sys.argv[1] if len(sys.argv) > 1 else "svalbard_spring"
    if case_key not in CASE_MAP:
        raise SystemExit(f"Unknown case '{case_key}'. Choose from: {', '.join(sorted(CASE_MAP))}")
    cfg = CASE_MAP[case_key]

    paths_path = RESULTS_TABLE_DIR / f"{cfg['route_prefix']}_paths.csv"
    weights_path = RESULTS_TABLE_DIR / f"{cfg['route_prefix']}_weight_sets.csv"
    output_rmse_path = RESULTS_TABLE_DIR / f"{cfg['eval_prefix']}_rmse.csv"
    output_band_path = RESULTS_TABLE_DIR / f"{cfg['eval_prefix']}_route_band_summaries.csv"
    figure_top_path = RESULTS_FIGURE_DIR / f"{cfg['eval_prefix']}_top20_rmse_routes.png"
    figure_coeff_path = RESULTS_FIGURE_DIR / f"{cfg['eval_prefix']}_top_rmse_coefficient_boxplots.png"
    report_path = RESULTS_REPORT_DIR / f"{cfg['eval_prefix']}_rmse.md"

    path_df = pd.read_csv(paths_path)
    weights_df = pd.read_csv(weights_path)
    benchmark = pd.read_csv(cfg["benchmark_path"])
    old_coeffs = load_old_paper_coefficients()
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
        merged["lon_error_deg"] = merged["route_lon_median"] - merged["benchmark_lon_median"]
        merged["lon_error_km"] = lon_degree_km_at_lat(merged["benchmark_lat_median"], merged["lon_error_deg"])
        merged["squared_lon_error_km"] = merged["lon_error_km"] ** 2
        valid = merged.dropna(subset=["route_lon_median", "benchmark_lon_median", "benchmark_lat_median"])
        rmse = float(np.sqrt(valid["squared_lon_error_km"].mean())) if not valid.empty else np.nan
        n_bands = int(len(valid))
        band_rows.extend(merged.to_dict(orient="records"))
        rmse_rows.append({"behavior": behavior, "rmse_km": rmse, "n_compared_bands": n_bands})
        route_lines[behavior] = points

    band_df = pd.DataFrame(band_rows)
    rmse_df = pd.DataFrame(rmse_rows).merge(weights_df, on="behavior", how="left").sort_values(["rmse_km", "behavior"])

    output_rmse_path.parent.mkdir(parents=True, exist_ok=True)
    figure_top_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    rmse_df.to_csv(output_rmse_path, index=False)
    band_df.to_csv(output_band_path, index=False)

    top20 = rmse_df.head(20).copy()
    env["has_wind_support"] = ~(env[["u10", "v10"]].isna().all(axis=1))
    masked = env.loc[~env["has_wind_support"]].copy()
    supported = env.loc[env["has_wind_support"]].copy()

    fig, ax = plt.subplots(figsize=(8.2, 10.5), constrained_layout=True)
    ax.scatter(masked["lon"], masked["lat"], s=90, marker="h", color="#c8b08f", alpha=0.75, linewidths=0)
    ax.scatter(supported["lon"], supported["lat"], s=65, marker="h", color="#dceaf7", alpha=0.18, linewidths=0)
    ax.plot(benchmark["benchmark_lon_median"], benchmark["benchmark_lat_median"], color="black", linewidth=2.8, label="Benchmark 10° mean")
    colors = plt.cm.viridis(np.linspace(0.15, 0.95, max(len(top20), 1)))
    for color, row in zip(colors, top20.itertuples(index=False)):
        points = route_lines[row.behavior]
        ax.plot(points["lon"], points["lat"], color=color, linewidth=1.4, alpha=0.75, label=f"{row.behavior} RMSE={row.rmse_km:.0f} km")
    ax.set_title(f"Top 20 RMSE LCPs versus {cfg['title_label']} benchmark")
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=7)
    fig.savefig(figure_top_path, dpi=170)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 6.8), constrained_layout=True, sharey=True)
    labels = ["a_wind", "b_crosswind", "c_distance", "d_food"]
    colors = ["#4c78a8", "#72b7b2", "#f58518", "#54a24b"]
    top20_data = [top20["a_wind"], top20["b_crosswind"], top20["c_distance"], top20["d_food"]]
    old_data = [old_coeffs["a_wind"], old_coeffs["b_crosswind"], old_coeffs["c_distance"], old_coeffs["d_food"]]

    left = axes[0].boxplot(top20_data, patch_artist=True, tick_labels=labels)
    right = axes[1].boxplot(old_data, patch_artist=True, tick_labels=labels)
    for box_group in (left, right):
        for patch, color in zip(box_group["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.75)
    axes[0].set_title(f"Top 20 H3 routes, {cfg['title_label']}")
    axes[1].set_title("Old paper 195-behavior set")
    axes[0].set_ylabel("Coefficient value")
    axes[0].set_ylim(0, 1)
    axes[1].set_ylim(0, 1)
    fig.suptitle(f"Coefficient distributions, {cfg['title_label']} top 20 versus old paper behavior set")
    fig.savefig(figure_coeff_path, dpi=170)
    plt.close(fig)

    best = rmse_df.iloc[0]
    report = f'''# Evaluate full bounded {cfg['title_label']} sweep by RMSE

## Question
Which behaviors from the saved 216-route full bounded {cfg['title_label']} sweep best recreate the benchmark flyway summary?

## Evaluation rule
For each simulated route:
- reconstruct the route as an ordered polyline from saved route coordinates
- summarize the route by 10° latitude bands
- compute the median longitude of the simulated route within each band
- compare that to the benchmark median longitude in the same band
- compute RMSE in km across all bands where both benchmark and simulated values are available

## Outputs
- RMSE table: `{output_rmse_path.relative_to(PROJECT_ROOT)}`
- per-band route summaries: `{output_band_path.relative_to(PROJECT_ROOT)}`
- top-20 route map: `{figure_top_path.relative_to(PROJECT_ROOT)}`
- coefficient boxplots: `{figure_coeff_path.relative_to(PROJECT_ROOT)}`

## Quick-look figures

![Top 20 RMSE LCPs](../figures/{figure_top_path.name})

![Coefficient boxplots](../figures/{figure_coeff_path.name})

## Main result
- lowest-RMSE behavior: **{best['behavior']}**
- lowest RMSE: **{best['rmse_km']:.1f} km**
- compared latitude bands: **{int(best['n_compared_bands'])}**
- weights: **({best['a_wind']:.1f}, {best['b_crosswind']:.1f}, {best['c_distance']:.1f}, {best['d_food']:.1f})**

## Efficiency note
This evaluation reuses saved route outputs and does not rerun Dijkstra simulations.
'''
    report_path.write_text(report)

    print(f"Evaluated full bounded {case_key} sweep by RMSE")
    print(f"behaviors ranked: {len(rmse_df)}")
    print(f"best behavior: {best['behavior']}")
    print(f"best RMSE: {best['rmse_km']:.1f} km")
    print(f"report: {report_path}")


if __name__ == "__main__":
    main()
