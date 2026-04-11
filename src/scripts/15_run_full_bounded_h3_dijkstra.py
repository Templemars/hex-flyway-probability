#!/usr/bin/env python3
"""
Run the full bounded H3 Dijkstra behavior sweep for the Svalbard spring case.

Important note:
This script uses the currently documented bounded coefficient grid:
- a (wind) in 0.0..1.0 by 0.1
- b (crosswind) in 0.0..0.5 by 0.1
- c (distance) in 0.0..1.0 by 0.1
- d (food) in 0.0..0.5 by 0.1
- a + b + c + d = 1.0

Under these rules the sweep contains 216 combinations.
This is not assumed to be identical to the paper's 195-filtered set.
"""

from __future__ import annotations

from itertools import product
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPONENT_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_edge_cost_components_res3.csv"
ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_environment_res3.csv"
SS_BENCHMARK_PATH = PROJECT_ROOT / "data" / "raw" / "benchmark_from_2025" / "gdf_SS_10.csv"

OUTPUT_ROUTE_PATH = PROJECT_ROOT / "results" / "tables" / "15_svalbard_full_bounded_dijkstra_paths.csv"
OUTPUT_SUMMARY_PATH = PROJECT_ROOT / "results" / "tables" / "15_svalbard_full_bounded_dijkstra_summary.csv"
OUTPUT_WEIGHTS_PATH = PROJECT_ROOT / "results" / "tables" / "15_svalbard_full_bounded_dijkstra_weight_sets.csv"
OUTPUT_ENDPOINTS_PATH = PROJECT_ROOT / "results" / "tables" / "15_svalbard_full_bounded_dijkstra_endpoints.csv"
FIGURE_PATH = PROJECT_ROOT / "results" / "figures" / "15_svalbard_full_bounded_dijkstra_routes.png"
FIGURE_DENSITY_PATH = PROJECT_ROOT / "results" / "figures" / "15_svalbard_full_bounded_dijkstra_routes_transparent.png"
FIGURE_HEATMAP_PATH = PROJECT_ROOT / "results" / "figures" / "15_svalbard_full_bounded_dijkstra_point_density_heatmap.png"
REPORT_PATH = PROJECT_ROOT / "results" / "reports" / "15_run-full-bounded-h3-dijkstra.md"


def generate_weight_sets() -> list[tuple[str, float, float, float, float]]:
    values_a = [i / 10 for i in range(11)]
    values_b = [i / 10 for i in range(6)]
    values_c = [i / 10 for i in range(11)]
    values_d = [i / 10 for i in range(6)]
    weight_sets = []
    idx = 1
    for a, b, c, d in product(values_a, values_b, values_c, values_d):
        if abs((a + b + c + d) - 1.0) < 1e-9:
            weight_sets.append((f"behavior_{idx:03d}", a, b, c, d))
            idx += 1
    return weight_sets


def nearest_h3_cell(env: pd.DataFrame, lon: float, lat: float) -> str:
    distance = (env["lon"] - lon) ** 2 + (env["lat"] - lat) ** 2
    return str(env.loc[distance.idxmin(), "h3_cell"])


def derive_prototype_endpoints(benchmark: pd.DataFrame, env: pd.DataFrame) -> tuple[dict, dict]:
    start_point = benchmark.iloc[0]
    end_point = benchmark.iloc[-1]
    start_lon = float(start_point["lon_median10"])
    start_lat = float(start_point["lat_median10"])
    end_lon = float(end_point["lon_median10"])
    end_lat = float(end_point["lat_median10"])
    return (
        {
            "endpoint_role": "start",
            "benchmark_rule": "first_row_of_gdf_SS_10",
            "lon": start_lon,
            "lat": start_lat,
            "nearest_h3_cell": nearest_h3_cell(env, start_lon, start_lat),
        },
        {
            "endpoint_role": "end",
            "benchmark_rule": "last_row_of_gdf_SS_10",
            "lon": end_lon,
            "lat": end_lat,
            "nearest_h3_cell": nearest_h3_cell(env, end_lon, end_lat),
        },
    )


def build_graph(df: pd.DataFrame, cost_col: str) -> nx.DiGraph:
    graph = nx.DiGraph()
    for row in df.itertuples(index=False):
        graph.add_edge(
            row.source_h3,
            row.target_h3,
            weight=float(getattr(row, cost_col)),
            edge_distance_km=float(row.edge_distance_km),
            w_cost=float(row.w_cost),
            c_cost=float(row.c_cost),
            d_cost=float(row.d_cost),
            f_cost=float(row.f_cost),
            source_lon=float(row.source_lon),
            source_lat=float(row.source_lat),
            target_lon=float(row.target_lon),
            target_lat=float(row.target_lat),
        )
    return graph


def summarize_path(graph: nx.DiGraph, path: list[str], label: str) -> tuple[list[dict], dict]:
    path_rows = []
    total_distance = total_w = total_c = total_d = total_f = total_cost = 0.0
    for step_index, (u, v) in enumerate(zip(path[:-1], path[1:]), start=1):
        edge = graph[u][v]
        total_distance += edge["edge_distance_km"]
        total_w += edge["w_cost"]
        total_c += edge["c_cost"]
        total_d += edge["d_cost"]
        total_f += edge["f_cost"]
        total_cost += edge["weight"]
        path_rows.append(
            {
                "behavior": label,
                "step_index": step_index,
                "source_h3": u,
                "target_h3": v,
                "source_lon": edge["source_lon"],
                "source_lat": edge["source_lat"],
                "target_lon": edge["target_lon"],
                "target_lat": edge["target_lat"],
                "edge_distance_km": edge["edge_distance_km"],
                "w_cost": edge["w_cost"],
                "c_cost": edge["c_cost"],
                "d_cost": edge["d_cost"],
                "f_cost": edge["f_cost"],
                "total_edge_cost": edge["weight"],
            }
        )
    return path_rows, {
        "behavior": label,
        "n_steps": len(path) - 1,
        "total_distance_km": total_distance,
        "total_cost": total_cost,
        "mean_edge_distance_km": total_distance / max(len(path) - 1, 1),
        "sum_w_cost": total_w,
        "sum_c_cost": total_c,
        "sum_d_cost": total_d,
        "sum_f_cost": total_f,
    }


def main() -> None:
    weight_sets = generate_weight_sets()
    df = pd.read_csv(COMPONENT_PATH)
    env = pd.read_csv(ENV_PATH)
    benchmark = pd.read_csv(SS_BENCHMARK_PATH)

    env["has_wind_support"] = ~(env[["u10", "v10"]].isna().all(axis=1))
    water_cells = set(env.loc[env["has_wind_support"], "h3_cell"].astype(str))
    df = df[df["source_h3"].astype(str).isin(water_cells) & df["target_h3"].astype(str).isin(water_cells)].copy()

    start_record, end_record = derive_prototype_endpoints(benchmark, env)
    start_cell = start_record["nearest_h3_cell"]
    end_cell = end_record["nearest_h3_cell"]

    weights_df = pd.DataFrame(weight_sets, columns=["behavior", "a_wind", "b_crosswind", "c_distance", "d_food"])
    endpoints_df = pd.DataFrame([start_record, end_record])

    all_path_rows = []
    summaries = []
    failed_behaviors = []

    for behavior, a, b, c, d in weight_sets:
        run_df = df.copy()
        run_df["total_cost"] = a * run_df["w_cost"] + b * run_df["c_cost"] + c * run_df["d_cost"] + d * run_df["f_cost"]
        graph = build_graph(run_df, "total_cost")
        try:
            path = nx.shortest_path(graph, source=start_cell, target=end_cell, weight="weight")
        except Exception as exc:
            failed_behaviors.append({
                "behavior": behavior,
                "a_wind": a,
                "b_crosswind": b,
                "c_distance": c,
                "d_food": d,
                "status": "failed",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            })
            continue
        path_rows, summary = summarize_path(graph, path, behavior)
        summary.update({"a_wind": a, "b_crosswind": b, "c_distance": c, "d_food": d, "status": "ok"})
        all_path_rows.extend(path_rows)
        summaries.append(summary)

    path_df = pd.DataFrame(all_path_rows)
    summary_df = pd.DataFrame(summaries)
    failed_df = pd.DataFrame(failed_behaviors)
    if not summary_df.empty:
        summary_df = summary_df.sort_values("total_cost")

    OUTPUT_ROUTE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    path_df.to_csv(OUTPUT_ROUTE_PATH, index=False)
    summary_df.to_csv(OUTPUT_SUMMARY_PATH, index=False)
    weights_df.to_csv(OUTPUT_WEIGHTS_PATH, index=False)
    endpoints_df.to_csv(OUTPUT_ENDPOINTS_PATH, index=False)
    if not failed_df.empty:
        failed_df.to_csv(OUTPUT_SUMMARY_PATH.with_name("15_svalbard_full_bounded_dijkstra_failures.csv"), index=False)

    fig, ax = plt.subplots(figsize=(8.2, 10.5), constrained_layout=True)
    masked = env.loc[~env["has_wind_support"]].copy()
    supported = env.loc[env["has_wind_support"]].copy()
    ax.scatter(masked["lon"], masked["lat"], s=90, marker="h", color="#c8b08f", alpha=0.75, linewidths=0)
    ax.scatter(supported["lon"], supported["lat"], s=65, marker="h", color="#dceaf7", alpha=0.20, linewidths=0)
    for behavior, route in path_df.groupby("behavior"):
        lons = [route.iloc[0]["source_lon"]] + route["target_lon"].tolist()
        lats = [route.iloc[0]["source_lat"]] + route["target_lat"].tolist()
        ax.plot(lons, lats, color="#355f8d", linewidth=1.6, alpha=0.10)
    ax.scatter([start_record["lon"], end_record["lon"]], [start_record["lat"], end_record["lat"]], color="black", s=35, marker="x")
    ax.set_title("Full bounded H3 Dijkstra sweep, Svalbard spring")
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    fig.savefig(FIGURE_PATH, dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.2, 10.5), constrained_layout=True)
    ax.scatter(masked["lon"], masked["lat"], s=90, marker="h", color="#c8b08f", alpha=0.75, linewidths=0)
    ax.scatter(supported["lon"], supported["lat"], s=65, marker="h", color="#dceaf7", alpha=0.12, linewidths=0)
    for behavior, route in path_df.groupby("behavior"):
        lons = [route.iloc[0]["source_lon"]] + route["target_lon"].tolist()
        lats = [route.iloc[0]["source_lat"]] + route["target_lat"].tolist()
        ax.plot(lons, lats, color="black", linewidth=2.2, alpha=0.025)
    ax.scatter([start_record["lon"], end_record["lon"]], [start_record["lat"], end_record["lat"]], color="crimson", s=35, marker="x")
    ax.set_title("Full bounded H3 Dijkstra sweep, transparent overview")
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    fig.savefig(FIGURE_DENSITY_PATH, dpi=170)
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
- failed-behavior table when relevant: `results/tables/15_svalbard_full_bounded_dijkstra_failures.csv`
- route overview figure: `results/figures/15_svalbard_full_bounded_dijkstra_routes.png`
- transparent route overview figure: `results/figures/15_svalbard_full_bounded_dijkstra_routes_transparent.png`
- route-point density heatmap: `results/figures/15_svalbard_full_bounded_dijkstra_point_density_heatmap.png`

## Quick-look figures

![Full bounded H3 Dijkstra sweep](../figures/15_svalbard_full_bounded_dijkstra_routes.png)

![Full bounded H3 Dijkstra sweep, transparent overview](../figures/15_svalbard_full_bounded_dijkstra_routes_transparent.png)

![Full bounded H3 Dijkstra sweep, Atlantic point-density heatmap](../figures/15_svalbard_full_bounded_dijkstra_point_density_heatmap.png)

## Run summary
- number of tested behaviors: **{len(weights_df)}**
- number of successful route runs: **{0 if summary_df.empty else len(summary_df)}**
- number of failed route runs: **{0 if failed_df.empty else len(failed_df)}**

## Interpretation
This step creates the full candidate pool under the currently documented bounded coefficient rules. That matters because the main goal is not to identify the route with the lowest internal modeled path cost, but to generate the full set of candidate least-cost paths that can later be compared against the Svalbard spring benchmark flyway.

So the main value of this sweep is coverage. It ensures that later route-to-benchmark comparison is done against the whole bounded grid rather than a hand-picked subset. The overview plots are therefore not final results by themselves. They are a structural map of the available simulated route family under the current cost graph.

The key things to inspect visually are:
- whether the route family collapses into a few dominant corridors or fills a broad envelope
- whether some combinations appear to produce visibly implausible detours or extreme spread
- whether the route cloud suggests that the current graph and endpoint setup are capable of spanning the benchmark flyway geometry at all
- whether the semi-transparent wide-line plots and the point-density heatmap reveal concentrated corridor use or a much more diffuse route field across the Atlantic domain

## Next step
Use this full bounded route set as the candidate pool for the first explicit route-to-benchmark comparison against the Svalbard spring 10-degree mean flyway.
'''
    REPORT_PATH.write_text(report)

    print("Ran full bounded H3 Dijkstra sweep")
    print(f"tested behaviors: {len(weights_df)}")
    print(f"successful routes: {0 if summary_df.empty else len(summary_df)}")
    print(f"failed routes: {0 if failed_df.empty else len(failed_df)}")
    print(f"report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
