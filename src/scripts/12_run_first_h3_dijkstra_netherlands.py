#!/usr/bin/env python3
"""
Run the first H3 Dijkstra prototype for the Netherlands spring case.

This mirrors the explicit numbered prototype step used for Svalbard, but with
Netherlands spring benchmark endpoints and Netherlands-specific output names.
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
NS_BENCHMARK_PATH = PROJECT_ROOT / "data" / "raw" / "benchmark_from_2025" / "gdf_NS_10.csv"

OUTPUT_ROUTE_PATH = PROJECT_ROOT / "data" / "processed" / "routes" / "h3_dijkstra_netherlands_spring_paths.csv"
OUTPUT_SUMMARY_PATH = PROJECT_ROOT / "results" / "tables" / "12_netherlands_dijkstra_summary.csv"
OUTPUT_WEIGHTS_PATH = PROJECT_ROOT / "results" / "tables" / "12_netherlands_dijkstra_weight_sets.csv"
OUTPUT_ENDPOINTS_PATH = PROJECT_ROOT / "results" / "tables" / "12_netherlands_dijkstra_endpoints.csv"
OUTPUT_FAILURES_PATH = PROJECT_ROOT / "results" / "tables" / "12_netherlands_dijkstra_failures.csv"
FIGURE_PATH = PROJECT_ROOT / "results" / "figures" / "12_netherlands_dijkstra_routes.png"
OVERLAY_FIGURE_PATH = PROJECT_ROOT / "results" / "figures" / "12_netherlands_component_maps_with_lcps.png"
REPORT_PATH = PROJECT_ROOT / "results" / "reports" / "12_run-first-h3-dijkstra-netherlands.md"

WEIGHT_SETS = [
    ("support_only", 1.0, 0.0, 0.0, 0.0),
    ("crosswind_only", 0.0, 1.0, 0.0, 0.0),
    ("distance_only", 0.0, 0.0, 1.0, 0.0),
    ("food_only", 0.0, 0.0, 0.0, 1.0),
]


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
            "benchmark_rule": "first_row_of_gdf_NS_10",
            "lon": start_lon,
            "lat": start_lat,
            "nearest_h3_cell": nearest_h3_cell(env, start_lon, start_lat),
        },
        {
            "endpoint_role": "end",
            "benchmark_rule": "last_row_of_gdf_NS_10",
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


def draw_component_map_panel(ax: plt.Axes, df: pd.DataFrame, value_col: str, masked_df: pd.DataFrame, title: str, vmin: float, vmax: float):
    ax.scatter(masked_df["lon"], masked_df["lat"], s=75, marker="h", color="#c8b08f", alpha=0.55, linewidths=0)
    sc = ax.scatter(df["lon"], df["lat"], c=df[value_col], s=65, marker="h", cmap="viridis", linewidths=0, alpha=0.9, vmin=vmin, vmax=vmax)
    ax.set_title(title)
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    return sc


def main() -> None:
    df = pd.read_csv(COMPONENT_PATH)
    env = pd.read_csv(ENV_PATH)
    benchmark = pd.read_csv(NS_BENCHMARK_PATH)

    env["has_wind_support"] = ~(env[["u10", "v10"]].isna().all(axis=1))
    water_cells = set(env.loc[env["has_wind_support"], "h3_cell"].astype(str))
    df = df[df["source_h3"].astype(str).isin(water_cells) & df["target_h3"].astype(str).isin(water_cells)].copy()

    start_record, end_record = derive_prototype_endpoints(benchmark, env)
    start_cell = start_record["nearest_h3_cell"]
    end_cell = end_record["nearest_h3_cell"]

    weights_df = pd.DataFrame(WEIGHT_SETS, columns=["behavior", "a_wind", "b_crosswind", "c_distance", "d_food"])
    endpoints_df = pd.DataFrame([start_record, end_record])

    all_path_rows = []
    summaries = []
    failed_behaviors = []

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
        failed_df.to_csv(OUTPUT_FAILURES_PATH, index=False)

    fig, ax = plt.subplots(figsize=(8.2, 10.5), constrained_layout=True)
    masked = env.loc[~env["has_wind_support"]].copy()
    supported = env.loc[env["has_wind_support"]].copy()
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
    ax.set_title("First H3 Dijkstra prototype routes, Netherlands spring")
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
    crosswind = map_env["u10"].abs()
    food = np.log10(map_env["chlor_a"].clip(lower=map_env.loc[map_env["chlor_a"] > 0, "chlor_a"].min()))
    food = food.max() - food
    distance_constant = float(df["d_cost"].median())

    map_env["w_cost"] = northward_support.max() - northward_support
    map_env["c_cost"] = crosswind
    map_env["d_cost"] = distance_constant
    map_env["f_cost"] = food

    vmax = float(np.nanpercentile(np.concatenate([map_env[col].to_numpy() for col in ["w_cost", "c_cost", "d_cost", "f_cost"]]), 99))
    vmin = 0.0

    fig, axes = plt.subplots(2, 2, figsize=(11.5, 12.0), constrained_layout=True)
    axes = axes.flatten()
    for ax, behavior in zip(axes, ["support_only", "crosswind_only", "distance_only", "food_only"]):
        value_col, title = background_cols[behavior]
        sc = draw_component_map_panel(ax, map_env, value_col, masked, title, vmin, vmax)
        route = path_df[path_df["behavior"] == behavior]
        if not route.empty:
            lons = [route.iloc[0]["source_lon"]] + route["target_lon"].tolist()
            lats = [route.iloc[0]["source_lat"]] + route["target_lat"].tolist()
            ax.plot(lons, lats, color="crimson", linewidth=2.2)
            ax.scatter([start_record["lon"], end_record["lon"]], [start_record["lat"], end_record["lat"]], color="black", s=28, marker="x")
        cbar = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label("Standardized cost units")
    fig.savefig(OVERLAY_FIGURE_PATH, dpi=170)
    plt.close(fig)

    report = f'''# Run first H3 Dijkstra prototype, Netherlands spring

## Question
What do the four extreme single-factor prototype behaviors produce for the Netherlands spring case on the H3 cost graph?

## Endpoint rule used
- start point = first row of `gdf_NS_10.csv`
- end point = last row of `gdf_NS_10.csv`
- both matched to nearest H3 cells

## Outputs
- path table: `data/processed/routes/h3_dijkstra_netherlands_spring_paths.csv`
- route summary table: `results/tables/12_netherlands_dijkstra_summary.csv`
- weight table: `results/tables/12_netherlands_dijkstra_weight_sets.csv`
- endpoint table: `results/tables/12_netherlands_dijkstra_endpoints.csv`
- failed-behavior table when relevant: `results/tables/12_netherlands_dijkstra_failures.csv`
- route overview figure: `results/figures/12_netherlands_dijkstra_routes.png`
- component-overlay figure: `results/figures/12_netherlands_component_maps_with_lcps.png`

## Quick-look figures

![First Netherlands H3 Dijkstra routes](../figures/12_netherlands_dijkstra_routes.png)

![Netherlands component maps with LCPs](../figures/12_netherlands_component_maps_with_lcps.png)

## Run summary
- number of tested behaviors: **{len(weights_df)}**
- number of successful route runs: **{0 if summary_df.empty else len(summary_df)}**
- number of failed route runs: **{0 if failed_df.empty else len(failed_df)}**

## Interpretation
This is the Netherlands spring analogue of the first Svalbard H3 prototype. It is intended as a transparent diagnostic step that shows how the graph behaves under the four extreme single-factor routing assumptions before moving to broader coefficient mixtures or full sweeps.

## Next step
Use this prototype as the explicit Netherlands step-12 counterpart before broader Netherlands behavior sweeps or direct RMSE benchmarking.
'''
    REPORT_PATH.write_text(report)

    print("Ran first Netherlands H3 Dijkstra prototype")
    print(f"successful routes: {0 if summary_df.empty else len(summary_df)}")
    print(f"failed routes: {0 if failed_df.empty else len(failed_df)}")
    print(f"report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
