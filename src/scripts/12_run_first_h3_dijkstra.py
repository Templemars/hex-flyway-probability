#!/usr/bin/env python3
"""
Run the first H3 Dijkstra prototype for the Svalbard spring case.

Prototype assumptions
---------------------
- use the already agreed 10 prototype behavior combinations
- use NetworkX for the Dijkstra routine
- derive temporary representative endpoints from the benchmark route summary
- keep all steps transparent with explicit tables, figures, and report text
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPONENT_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_edge_cost_components_res3.csv"
ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_environment_res3.csv"
SS_BENCHMARK_PATH = PROJECT_ROOT / "data" / "raw" / "benchmark_from_2025" / "gdf_SS_10.csv"

OUTPUT_ROUTE_PATH = PROJECT_ROOT / "data" / "processed" / "routes" / "h3_dijkstra_svalbard_spring_paths.csv"
OUTPUT_SUMMARY_PATH = PROJECT_ROOT / "results" / "tables" / "12_svalbard_dijkstra_summary.csv"
OUTPUT_WEIGHTS_PATH = PROJECT_ROOT / "results" / "tables" / "12_svalbard_dijkstra_weight_sets.csv"
OUTPUT_ENDPOINTS_PATH = PROJECT_ROOT / "results" / "tables" / "12_svalbard_dijkstra_endpoints.csv"
FIGURE_PATH = PROJECT_ROOT / "results" / "figures" / "12_svalbard_dijkstra_routes.png"
REPORT_PATH = PROJECT_ROOT / "results" / "reports" / "12_run-first-h3-dijkstra.md"


WEIGHT_SETS = [
    ("wind_only", 1.0, 0.0, 0.0, 0.0),
    ("distance_only", 0.0, 0.0, 1.0, 0.0),
    ("wind_distance", 0.5, 0.0, 0.5, 0.0),
    ("wind_food", 0.5, 0.0, 0.0, 0.5),
    ("distance_food", 0.0, 0.0, 0.5, 0.5),
    ("wind_dominated", 0.7, 0.0, 0.3, 0.0),
    ("distance_food_leaning", 0.3, 0.0, 0.5, 0.2),
    ("wind_crosswind", 0.7, 0.1, 0.2, 0.0),
    ("balanced", 0.4, 0.1, 0.3, 0.2),
    ("crosswind_mix", 0.5, 0.2, 0.3, 0.0),
]


def nearest_h3_cell(env: pd.DataFrame, lon: float, lat: float) -> str:
    distance = (env["lon"] - lon) ** 2 + (env["lat"] - lat) ** 2
    return str(env.loc[distance.idxmin(), "h3_cell"])


def derive_prototype_endpoints(benchmark: pd.DataFrame, env: pd.DataFrame, n_points: int = 3) -> tuple[dict, dict]:
    start_points = benchmark.head(n_points)
    end_points = benchmark.tail(n_points)

    start_lon = float(start_points["lon_median10"].mean())
    start_lat = float(start_points["lat_median10"].mean())
    end_lon = float(end_points["lon_median10"].mean())
    end_lat = float(end_points["lat_median10"].mean())

    start_cell = nearest_h3_cell(env, start_lon, start_lat)
    end_cell = nearest_h3_cell(env, end_lon, end_lat)

    start_record = {
        "endpoint_role": "start",
        "n_benchmark_points_used": n_points,
        "lon": start_lon,
        "lat": start_lat,
        "nearest_h3_cell": start_cell,
    }
    end_record = {
        "endpoint_role": "end",
        "n_benchmark_points_used": n_points,
        "lon": end_lon,
        "lat": end_lat,
        "nearest_h3_cell": end_cell,
    }
    return start_record, end_record


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
    total_distance = 0.0
    total_w = 0.0
    total_c = 0.0
    total_d = 0.0
    total_f = 0.0
    total_cost = 0.0

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

    summary = {
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
    return path_rows, summary


def main() -> None:
    df = pd.read_csv(COMPONENT_PATH)
    env = pd.read_csv(ENV_PATH)
    benchmark = pd.read_csv(SS_BENCHMARK_PATH)

    start_record, end_record = derive_prototype_endpoints(benchmark, env, n_points=3)
    start_cell = start_record["nearest_h3_cell"]
    end_cell = end_record["nearest_h3_cell"]

    weights_df = pd.DataFrame(WEIGHT_SETS, columns=["behavior", "a_wind", "b_crosswind", "c_distance", "d_food"])
    endpoints_df = pd.DataFrame([start_record, end_record])

    all_path_rows: list[dict] = []
    summaries: list[dict] = []

    failed_behaviors: list[dict] = []

    for behavior, a, b, c, d in WEIGHT_SETS:
        cost_col = f"total_cost_{behavior}"
        df[cost_col] = a * df["w_cost"] + b * df["c_cost"] + c * df["d_cost"] + d * df["f_cost"]
        graph = build_graph(df, cost_col)
        try:
            path = nx.shortest_path(graph, source=start_cell, target=end_cell, weight="weight")
        except Exception as exc:
            failed_behaviors.append(
                {
                    "behavior": behavior,
                    "a_wind": a,
                    "b_crosswind": b,
                    "c_distance": c,
                    "d_food": d,
                    "status": "failed",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
            )
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
    OUTPUT_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    path_df.to_csv(OUTPUT_ROUTE_PATH, index=False)
    summary_df.to_csv(OUTPUT_SUMMARY_PATH, index=False)
    weights_df.to_csv(OUTPUT_WEIGHTS_PATH, index=False)
    endpoints_df.to_csv(OUTPUT_ENDPOINTS_PATH, index=False)
    if not failed_df.empty:
        failed_df.to_csv(OUTPUT_SUMMARY_PATH.with_name('12_svalbard_dijkstra_failures.csv'), index=False)

    fig, ax = plt.subplots(figsize=(11, 7), constrained_layout=True)
    sampled_background = env.iloc[::20]
    ax.scatter(sampled_background["lon"], sampled_background["lat"], s=2, color="lightgray", alpha=0.4)
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
    if successful_behaviors:
        ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8)
    fig.savefig(FIGURE_PATH, dpi=170)
    plt.close(fig)

    best = summary_df.iloc[0] if not summary_df.empty else None
    report = f'''# Run first H3 Dijkstra prototype

## Question
What do the first Svalbard spring Dijkstra routes look like across the agreed prototype behavior set?

## Input data
- `data/processed/grids/h3_edge_cost_components_res3.csv`
- `data/processed/grids/h3_environment_res3.csv`
- `data/raw/benchmark_from_2025/gdf_SS_10.csv`

## Behavior set used
The already agreed prototype behavior subset was used, with coefficient order:
- `a = wind`
- `b = crosswind`
- `c = distance`
- `d = food`

See:
- `results/tables/12_svalbard_dijkstra_weight_sets.csv`

## Prototype endpoint rule used
This first Dijkstra test uses a temporary transparent endpoint rule rather than a claimed final biological endpoint definition.

Implementation here:
- start point = mean of the first **3** benchmark summary points
- end point = mean of the last **3** benchmark summary points
- these mean points were then matched to the nearest H3 cells

See:
- `results/tables/12_svalbard_dijkstra_endpoints.csv`

## Outputs
- path table: `data/processed/routes/h3_dijkstra_svalbard_spring_paths.csv`
- route summary table: `results/tables/12_svalbard_dijkstra_summary.csv`
- failed-behavior table when relevant: `results/tables/12_svalbard_dijkstra_failures.csv`
- weight table: `results/tables/12_svalbard_dijkstra_weight_sets.csv`
- endpoint table: `results/tables/12_svalbard_dijkstra_endpoints.csv`
- route figure: `results/figures/12_svalbard_dijkstra_routes.png`

## Quick-look figure

![First H3 Dijkstra prototype routes](../figures/12_svalbard_dijkstra_routes.png)

## First reading
- number of tested behaviors: **{len(weights_df)}**
- successful route runs: **{0 if summary_df.empty else len(summary_df)}**
- failed route runs: **{0 if failed_df.empty else len(failed_df)}**

## Interpretation
This is the first end-to-end H3 route prototype: standardized edge costs are now being turned into actual destination-constrained paths. That is a meaningful transition from cost construction into flyway simulation.

The current routes should still be treated as prototype behavior diagnostics, not final biological claims, because:
- the endpoint rule is still provisional
- the distance term remains under explicit caution
- the behavior set is a deliberately small exploratory subset

A scientifically important issue also emerged immediately: at least one behavior can fail under package Dijkstra even when the cost components are non-negative. If that happens, it should be treated as a modeling red flag, not hidden as a technical nuisance.

## Points to watch
- if some routes look implausibly grid-aligned, revisit the distance red flag
- if behavior differences are weak, the component scaling or endpoint rule may be suppressing contrast
- if behavior differences are extreme, inspect whether one component is dominating too strongly

## Next step
Inspect the route table and summaries carefully, then decide whether the first endpoint rule is good enough to keep for the next round or should already be refined.
'''
    if best is not None:
        report += f"\nAdditional route summary:\n- best current prototype by total cost: **{best['behavior']}**\n- best prototype total cost: **{best['total_cost']:.3f}**\n- best prototype total distance: **{best['total_distance_km']:.1f} km**\n- best prototype step count: **{int(best['n_steps'])}**\n"
    if not failed_df.empty:
        report += "\nFailure note:\n- at least one prototype behavior failed during package Dijkstra and has been written to `results/tables/12_svalbard_dijkstra_failures.csv` for inspection\n"
    REPORT_PATH.write_text(report)

    print("Ran first H3 Dijkstra prototype")
    print(f"start cell: {start_cell}")
    print(f"end cell: {end_cell}")
    if best is not None:
        print(f"best behavior: {best['behavior']}")
    if not failed_df.empty:
        print(f"failed behaviors: {len(failed_df)}")
    print(f"report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
