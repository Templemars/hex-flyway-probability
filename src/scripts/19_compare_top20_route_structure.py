#!/usr/bin/env python3
"""
Compare top-20 route geometry structure between Svalbard spring and Netherlands
spring using saved outputs only.
"""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from flyway_h3.workflow_utils import assign_lat_band, route_points_from_group


TABLE_DIR = PROJECT_ROOT / "results" / "tables"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"
REPORT_DIR = PROJECT_ROOT / "results" / "reports"

SVALBARD_TOP20 = TABLE_DIR / "17_svalbard_top20_rmse_behaviors.csv"
NETHERLANDS_TOP20 = TABLE_DIR / "17_netherlands_top20_rmse_behaviors.csv"
SVALBARD_PATHS = TABLE_DIR / "15_svalbard_full_bounded_dijkstra_paths.csv"
NETHERLANDS_PATHS = TABLE_DIR / "15_netherlands_full_bounded_dijkstra_paths.csv"
SVALBARD_BENCH = PROJECT_ROOT / "data" / "raw" / "benchmark_from_2025" / "gdf_SS_10.csv"
NETHERLANDS_BENCH = PROJECT_ROOT / "data" / "raw" / "benchmark_from_2025" / "gdf_NS_10.csv"

OUTPUT_SPREAD = TABLE_DIR / "19_svalbard_netherlands_top20_route_spread.csv"
FIGURE_OVERLAY = FIGURE_DIR / "19_svalbard_netherlands_top20_route_overlays.png"
FIGURE_SPREAD = FIGURE_DIR / "19_svalbard_netherlands_top20_route_spread.png"
FIGURE_ENVELOPE = FIGURE_DIR / "19_svalbard_netherlands_top20_benchmark_envelopes.png"
REPORT_PATH = REPORT_DIR / "19_compare-top20-route-structure-svalbard-netherlands-spring.md"


def build_top20_points(paths_path: Path, top20_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    paths = pd.read_csv(paths_path)
    top20 = pd.read_csv(top20_path)
    keep = set(top20["behavior"].tolist())
    rows = []
    for behavior, route in paths.groupby("behavior"):
        if behavior not in keep:
            continue
        pts = route_points_from_group(route)
        pts["behavior"] = behavior
        pts["point_index"] = np.arange(len(pts))
        pts["lat_band"] = assign_lat_band(pts["lat"])
        rows.append(pts)
    point_df = pd.concat(rows, ignore_index=True)
    return point_df, top20


def summarize_spread(point_df: pd.DataFrame, label: str) -> pd.DataFrame:
    out = (
        point_df.dropna(subset=["lat_band"])
        .groupby("lat_band")
        .agg(
            route_lat_median=("lat", "median"),
            lon_p10=("lon", lambda s: float(np.percentile(s, 10))),
            lon_p50=("lon", "median"),
            lon_p90=("lon", lambda s: float(np.percentile(s, 90))),
            n_points=("lon", "size"),
        )
        .reset_index()
    )
    out["population"] = label
    out["lon_spread_p90_p10"] = out["lon_p90"] - out["lon_p10"]
    return out


def main() -> None:
    svalbard_points, svalbard_top20 = build_top20_points(SVALBARD_PATHS, SVALBARD_TOP20)
    nl_points, nl_top20 = build_top20_points(NETHERLANDS_PATHS, NETHERLANDS_TOP20)
    svalbard_bench = pd.read_csv(SVALBARD_BENCH)
    nl_bench = pd.read_csv(NETHERLANDS_BENCH)

    svalbard_spread = summarize_spread(svalbard_points, "Svalbard spring")
    nl_spread = summarize_spread(nl_points, "Netherlands spring")
    spread_df = pd.concat([svalbard_spread, nl_spread], ignore_index=True)

    OUTPUT_SPREAD.parent.mkdir(parents=True, exist_ok=True)
    FIGURE_OVERLAY.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    spread_df.to_csv(OUTPUT_SPREAD, index=False)

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 8.8), constrained_layout=True, sharex=True, sharey=True)
    for ax, points, bench, title in [
        (axes[0], svalbard_points, svalbard_bench, "Svalbard spring top 20"),
        (axes[1], nl_points, nl_bench, "Netherlands spring top 20"),
    ]:
        for _, route in points.groupby("behavior"):
            ax.plot(route["lon"], route["lat"], color="#355f8d", linewidth=1.8, alpha=0.18)
        ax.plot(bench["lon_median10"], bench["lat_median10"], color="black", linewidth=2.8)
        ax.set_title(title)
        ax.set_xlabel("Longitude (degrees)")
        ax.set_ylabel("Latitude (degrees)")
        ax.set_xlim(-95, 35)
        ax.set_ylim(-80, 85)
    fig.savefig(FIGURE_OVERLAY, dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.8, 6.4), constrained_layout=True)
    for df, color, label in [
        (svalbard_spread, "#4c78a8", "Svalbard spring"),
        (nl_spread, "#f58518", "Netherlands spring"),
    ]:
        ax.plot(df["lon_spread_p90_p10"], df["route_lat_median"], color=color, linewidth=2.5, label=label)
    ax.set_xlabel("Top-20 longitude spread, P90 minus P10 (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_title("Top-20 route spread by latitude band")
    ax.legend()
    fig.savefig(FIGURE_SPREAD, dpi=170)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 6.8), constrained_layout=True, sharey=True)
    for ax, spread, bench, color, title in [
        (axes[0], svalbard_spread, svalbard_bench, "#4c78a8", "Svalbard spring"),
        (axes[1], nl_spread, nl_bench, "#f58518", "Netherlands spring"),
    ]:
        ax.fill_betweenx(spread["route_lat_median"], spread["lon_p10"], spread["lon_p90"], color=color, alpha=0.28, label="Top-20 envelope")
        ax.plot(spread["lon_p50"], spread["route_lat_median"], color=color, linewidth=2.3, label="Top-20 median route")
        ax.plot(bench["lon_median10"], bench["lat_median10"], color="black", linewidth=2.5, label="Benchmark median")
        ax.set_title(title)
        ax.set_xlabel("Longitude (degrees)")
        ax.set_ylabel("Latitude (degrees)")
        ax.legend(fontsize=8)
    fig.savefig(FIGURE_ENVELOPE, dpi=170)
    plt.close(fig)

    svalbard_mean_spread = float(svalbard_spread["lon_spread_p90_p10"].mean())
    nl_mean_spread = float(nl_spread["lon_spread_p90_p10"].mean())
    svalbard_max_band = svalbard_spread.sort_values("lon_spread_p90_p10", ascending=False).iloc[0]
    nl_max_band = nl_spread.sort_values("lon_spread_p90_p10", ascending=False).iloc[0]

    report = f'''# Compare top-20 route structure, Svalbard spring versus Netherlands spring

## Question
How do the top 20 lowest-RMSE route families differ structurally between Svalbard spring and Netherlands spring?

## Inputs
- `results/tables/17_svalbard_top20_rmse_behaviors.csv`
- `results/tables/17_netherlands_top20_rmse_behaviors.csv`
- `results/tables/15_svalbard_full_bounded_dijkstra_paths.csv`
- `results/tables/15_netherlands_full_bounded_dijkstra_paths.csv`
- benchmark summaries `gdf_SS_10.csv` and `gdf_NS_10.csv`

## Outputs
- spread table: `results/tables/19_svalbard_netherlands_top20_route_spread.csv`
- overlay figure: `results/figures/19_svalbard_netherlands_top20_route_overlays.png`
- spread figure: `results/figures/19_svalbard_netherlands_top20_route_spread.png`
- benchmark-envelope figure: `results/figures/19_svalbard_netherlands_top20_benchmark_envelopes.png`

## Quick-look figures

![Top-20 route overlays](../figures/19_svalbard_netherlands_top20_route_overlays.png)

![Top-20 spread comparison](../figures/19_svalbard_netherlands_top20_route_spread.png)

![Benchmark versus top-20 envelopes](../figures/19_svalbard_netherlands_top20_benchmark_envelopes.png)

## Main structural comparison
- mean top-20 longitude spread across latitude bands, **Svalbard spring**: **{svalbard_mean_spread:.2f} degrees**
- mean top-20 longitude spread across latitude bands, **Netherlands spring**: **{nl_mean_spread:.2f} degrees**
- widest Svalbard top-20 band: **{svalbard_max_band['lat_band']}** with spread **{svalbard_max_band['lon_spread_p90_p10']:.2f} degrees**
- widest Netherlands top-20 band: **{nl_max_band['lat_band']}** with spread **{nl_max_band['lon_spread_p90_p10']:.2f} degrees**

## Interpretation
This step moves from coefficient comparison to route-family geometry. That matters because two populations can differ in top-ranked coefficients either because they genuinely prefer different movement regimes, or because their benchmark route geometries place different structural demands on the model.

The route-overlay figure shows whether the top 20 good solutions form a tight corridor or a broad family in each population. The spread-by-latitude figure then makes that explicit by showing where route uncertainty or flexibility is largest. The benchmark-envelope figure helps assess whether the benchmark line sits near the center of the good-solution family or closer to one side of the envelope.

If one population has a much wider top-20 envelope, that suggests the benchmark metric tolerates a broader family of good solutions there. If the envelope is tight, the benchmark is selecting a more specific route geometry. That distinction helps explain why different coefficient structures can survive among the top RMSE solutions.

## Efficiency note
This comparison uses saved top-20 route outputs only and does not rerun route simulations.
'''
    REPORT_PATH.write_text(report)

    print("Compared top-20 route structure for Svalbard and Netherlands spring")
    print(f"Svalbard mean spread: {svalbard_mean_spread:.2f} degrees")
    print(f"Netherlands mean spread: {nl_mean_spread:.2f} degrees")
    print(f"report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
