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
OVERLAY_FIGURE_PATH = PROJECT_ROOT / "results" / "figures" / "12_component_maps_with_lcps.png"
REPORT_PATH = PROJECT_ROOT / "results" / "reports" / "12_run-first-h3-dijkstra.md"


WEIGHT_SETS = [
    ("support_only", 1.0, 0.0, 0.0, 0.0),
    ("crosswind_only", 0.0, 1.0, 0.0, 0.0),
    ("distance_only", 0.0, 0.0, 1.0, 0.0),
    ("food_only", 0.0, 0.0, 0.0, 1.0),
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


def draw_component_map_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    value_col: str,
    masked_df: pd.DataFrame,
    title: str,
    vmin: float,
    vmax: float,
):
    ax.scatter(masked_df["lon"], masked_df["lat"], s=75, marker="h", color="#c8b08f", alpha=0.55, linewidths=0)
    sc = ax.scatter(
        df["lon"],
        df["lat"],
        c=df[value_col],
        s=65,
        marker="h",
        cmap="viridis",
        linewidths=0,
        alpha=0.9,
        vmin=vmin,
        vmax=vmax,
    )
    ax.set_title(title)
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    return sc


def main() -> None:
    df = pd.read_csv(COMPONENT_PATH)
    env = pd.read_csv(ENV_PATH)
    benchmark = pd.read_csv(SS_BENCHMARK_PATH)

    # Prototype routing mask based on the benchmark ERA5 wind support.
    # Cells without wind support in the transferred benchmark dataset are excluded.
    env["has_wind_support"] = ~(env[["u10", "v10"]].isna().all(axis=1))
    water_cells = set(env.loc[env["has_wind_support"], "h3_cell"].astype(str))
    df = df[df["source_h3"].astype(str).isin(water_cells) & df["target_h3"].astype(str).isin(water_cells)].copy()

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

    fig, ax = plt.subplots(figsize=(8.2, 10.5), constrained_layout=True)
    masked_background = env.copy()
    masked = masked_background.loc[~masked_background["has_wind_support"]].copy()
    supported = masked_background.loc[masked_background["has_wind_support"]].copy()
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
    ax.set_title("First H3 Dijkstra prototype routes, Svalbard spring")
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    if successful_behaviors:
        ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8)
    fig.savefig(FIGURE_PATH, dpi=170)
    plt.close(fig)

    # Diagnostic component maps with corresponding single-factor least-cost paths overlaid.
    background_cols = {
        "support_only": ("w_cost", "Support cost background with support-only LCP"),
        "crosswind_only": ("c_cost", "Crosswind cost background with crosswind-only LCP"),
        "distance_only": ("d_cost", "Distance cost background with distance-only LCP"),
        "food_only": ("f_cost", "Food cost background with food-only LCP"),
    }

    map_env = env.loc[env["has_wind_support"], ["h3_cell", "lon", "lat", "u10", "v10", "chlor_a"]].copy()
    northward_support = map_env["v10"]
    map_env["w_cost"] = 100.0 * np.abs(northward_support - np.nanpercentile(northward_support.to_numpy(), 99)) / np.nanpercentile(np.abs(northward_support - np.nanpercentile(northward_support.to_numpy(), 99)), 99)
    map_env["c_cost"] = 100.0 * np.abs(map_env["u10"]) / np.nanpercentile(np.abs(map_env["u10"]).to_numpy(), 99)
    northward_distance_lookup = df.groupby("source_h3", as_index=False)["d_cost"].first()
    map_env = map_env.merge(northward_distance_lookup, left_on="h3_cell", right_on="source_h3", how="left")
    map_env["f_cost"] = 100.0 * np.abs(np.where(np.log(map_env["chlor_a"].clip(lower=map_env.loc[map_env["chlor_a"] > 0, "chlor_a"].min())) <= -1, np.log(map_env["chlor_a"].clip(lower=map_env.loc[map_env["chlor_a"] > 0, "chlor_a"].min())), -1) + 1) / np.nanpercentile(np.abs(np.where(np.log(map_env["chlor_a"].clip(lower=map_env.loc[map_env["chlor_a"] > 0, "chlor_a"].min())) <= -1, np.log(map_env["chlor_a"].clip(lower=map_env.loc[map_env["chlor_a"] > 0, "chlor_a"].min())), -1) + 1), 99)
    shared_overlay_max = float(np.nanpercentile(map_env[["w_cost", "c_cost", "d_cost", "f_cost"]].to_numpy(), 99))

    fig, axes = plt.subplots(2, 2, figsize=(11, 13), constrained_layout=True)
    for ax, behavior in zip(axes.ravel(), ["support_only", "crosswind_only", "distance_only", "food_only"]):
        value_col, title = background_cols[behavior]
        sc = draw_component_map_panel(ax, map_env, value_col, masked, title, 0.0, shared_overlay_max)
        route = path_df[path_df["behavior"] == behavior]
        if not route.empty:
            lons = [route.iloc[0]["source_lon"]] + route["target_lon"].tolist()
            lats = [route.iloc[0]["source_lat"]] + route["target_lat"].tolist()
            ax.plot(lons, lats, color="crimson", linewidth=2.0)
        cbar = fig.colorbar(sc, ax=ax)
        cbar.set_label(f"Standardized cost (SCU), shared scale 0 to {shared_overlay_max:.1f}")
    fig.savefig(OVERLAY_FIGURE_PATH, dpi=170)
    plt.close(fig)

    best = summary_df.iloc[0] if not summary_df.empty else None
    report = f'''# Run first H3 Dijkstra prototype

## Question
What happens when the first Svalbard spring H3 Dijkstra tests are run under four extreme single-factor behaviors, using the current prototype endpoint rule and the ERA5-supported routing mask?

## Input data
- `data/processed/grids/h3_edge_cost_components_res3.csv`
- `data/processed/grids/h3_environment_res3.csv`
- `data/raw/benchmark_from_2025/gdf_SS_10.csv`

## Tested single-factor behaviors
This first extreme-behavior batch uses only four single-factor cases, with coefficient order:
- `a = wind support`
- `b = crosswind`
- `c = distance`
- `d = food`

The tested behaviors are:
- `support_only = (1.0, 0.0, 0.0, 0.0)`
- `crosswind_only = (0.0, 1.0, 0.0, 0.0)`
- `distance_only = (0.0, 0.0, 1.0, 0.0)`
- `food_only = (0.0, 0.0, 0.0, 1.0)`

See:
- `results/tables/12_svalbard_dijkstra_weight_sets.csv`

## Routing mask used
Following the paper's overwater-routing stance, the first H3 prototype now uses the transferred benchmark ERA5 support as its routing-domain mask.

Implementation here:
- identify H3 cells that have valid transferred `u10` and `v10` values in the benchmark environmental table
- keep only edges whose source and target both lie inside that supported domain
- show the supported versus masked cells directly on the route figure using different colors and gridcell-like hex markers rather than centroid dots

Interpretation:
- this is a routing-domain mask based on the environmental support actually used in the cost construction
- it should be interpreted as a benchmark ERA5-supported domain for the prototype, not yet as a final polished biological mask definition

## Prototype endpoint rule used
This first Dijkstra test still uses a pragmatic temporary endpoint rule rather than a final biological endpoint definition.

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
- diagnostic overlay figure: `results/figures/12_component_maps_with_lcps.png`

Map framing:
- the route figure is focused on the Atlantic domain
- the figure now uses a more portrait-oriented layout to make the trans-Atlantic route geometry easier to inspect
- the routing mask is visualized with gridcell-like hex markers rather than sparse centroid dots, so the supported and masked regions read more like spatial cells

## Quick-look figure

![First H3 Dijkstra prototype routes](../figures/12_svalbard_dijkstra_routes.png)

![Diagnostic component maps with corresponding least-cost paths](../figures/12_component_maps_with_lcps.png)

## Why the overlay figure is useful, and its limit
The overlay figure is scientifically useful as a **diagnostic comparison**.
It helps us check whether each single-factor route is moving through visually low-cost regions of the corresponding component background.
The four panels reuse the older mapping rule of a shared color scale from `0` to the shared `P99` across the displayed component backgrounds, and each panel has its own explicit colorbar for readability.

However, it should not be interpreted too literally as the exact optimization surface used by Dijkstra, because:
- the real routing is done on the directed edge graph
- the background panels are cell-level diagnostic surfaces
- the wind backgrounds are simplified visualization surfaces rather than the full edge-based object

So this figure is appropriate for interpretation, but it remains a diagnostic comparison rather than a perfect one-to-one representation of the graph optimization problem.

## Run status summary
- number of tested behaviors: **{len(weights_df)}**
- number of successful route runs: **{0 if summary_df.empty else len(summary_df)}**
- number of failed route runs: **{0 if failed_df.empty else len(failed_df)}**

## Interpretation
This is the first end-to-end H3 route prototype with an explicit ERA5-supported routing domain. That is an important milestone, because the project has now moved from component construction into actual destination-constrained path generation.

At the same time, the current outputs should still be treated as diagnostic prototype results rather than validated flyway simulations. That caution is needed because:
- the endpoint rule is still provisional
- the distance term remains under explicit caution
- the current batch uses deliberately extreme single-factor behaviors
- some behaviors do not yet yield stable successful Dijkstra results under the present setup

This means the present run is most useful for exposing model behavior and failure modes, not for making strong biological claims.

## What to pay attention to
- whether the successful routes look strongly grid-aligned
- whether the single-factor runs differ in interpretable ways or collapse toward similar paths
- whether failures cluster in particular components, which would suggest component-specific pathologies rather than a generic routing issue
- whether the provisional endpoint rule is suppressing or exaggerating differences among behaviors

## Next step
Inspect the successful and failed single-factor runs explicitly, then decide whether to refine the endpoint definition, modify the tested behavior set, or adjust the cost setup before moving further into comparison against the benchmark flyway.
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
