#!/usr/bin/env python3
"""
Run a compact endpoint-sensitivity experiment for the Svalbard spring H3 prototype.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import h3


PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPONENT_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_edge_cost_components_res3.csv"
ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_environment_res3.csv"
OUTPUT_COORDS_PATH = PROJECT_ROOT / "results" / "tables" / "13_svalbard_endpoint_sensitivity_coordinates.csv"
OUTPUT_ENDPOINTS_PATH = PROJECT_ROOT / "results" / "tables" / "13_svalbard_endpoint_sensitivity_endpoints.csv"
FIGURE_PATH = PROJECT_ROOT / "results" / "figures" / "13_svalbard_endpoint_sensitivity_routes.png"
REPORT_PATH = PROJECT_ROOT / "results" / "reports" / "13_endpoint-sensitivity-svalbard.md"

REFERENCE_START = "83eea8fffffffff"
REFERENCE_END = "83076bfffffffff"
WEIGHT_SETS = [
    ("support_only", 1.0, 0.0, 0.0, 0.0),
    ("crosswind_only", 0.0, 1.0, 0.0, 0.0),
    ("distance_only", 0.0, 0.0, 1.0, 0.0),
    ("food_only", 0.0, 0.0, 0.0, 1.0),
]


def build_graph(df: pd.DataFrame) -> nx.DiGraph:
    graph = nx.DiGraph()
    for row in df.itertuples(index=False):
        graph.add_edge(
            row.source_h3,
            row.target_h3,
            weight=float(row.total_cost),
            source_lon=float(row.source_lon),
            source_lat=float(row.source_lat),
            target_lon=float(row.target_lon),
            target_lat=float(row.target_lat),
        )
    return graph


def route_to_rows(behavior: str, route_name: str, path: list[str], graph: nx.DiGraph) -> list[dict]:
    rows = []
    if len(path) < 2:
        return rows
    first = graph[path[0]][path[1]]
    rows.append({"behavior": behavior, "route_name": route_name, "point_index": 0, "lon": first["source_lon"], "lat": first["source_lat"]})
    for i, (u, v) in enumerate(zip(path[:-1], path[1:]), start=1):
        edge = graph[u][v]
        rows.append({"behavior": behavior, "route_name": route_name, "point_index": i, "lon": edge["target_lon"], "lat": edge["target_lat"]})
    return rows


def draw_component_map_panel(ax, df, value_col, masked_df, title, vmin, vmax):
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
    env["has_wind_support"] = ~(env[["u10", "v10"]].isna().all(axis=1))
    water_cells = set(env.loc[env["has_wind_support"], "h3_cell"].astype(str))
    df = df[df["source_h3"].astype(str).isin(water_cells) & df["target_h3"].astype(str).isin(water_cells)].copy()

    start_candidates = sorted(h3.grid_disk(REFERENCE_START, 1))
    end_candidates = sorted(h3.grid_disk(REFERENCE_END, 1))

    endpoint_rows = []
    coord_rows = []
    plotted_routes = {behavior: [] for behavior, *_ in WEIGHT_SETS}

    for behavior, a, b, c, d in WEIGHT_SETS:
        run_df = df.copy()
        run_df["total_cost"] = a * run_df["w_cost"] + b * run_df["c_cost"] + c * run_df["d_cost"] + d * run_df["f_cost"]
        graph = build_graph(run_df)

        for start_cell in start_candidates:
            for end_cell in end_candidates:
                route_name = f"start_{start_cell}_end_{end_cell}"
                is_reference = start_cell == REFERENCE_START and end_cell == REFERENCE_END
                if start_cell not in graph or end_cell not in graph:
                    endpoint_rows.append({
                        "behavior": behavior,
                        "route_name": route_name,
                        "start_h3": start_cell,
                        "end_h3": end_cell,
                        "is_reference": is_reference,
                        "status": "missing_node",
                    })
                    continue
                try:
                    path = nx.shortest_path(graph, source=start_cell, target=end_cell, weight="weight")
                except Exception as exc:
                    endpoint_rows.append({
                        "behavior": behavior,
                        "route_name": route_name,
                        "start_h3": start_cell,
                        "end_h3": end_cell,
                        "is_reference": is_reference,
                        "status": type(exc).__name__,
                    })
                    continue

                endpoint_rows.append({
                    "behavior": behavior,
                    "route_name": route_name,
                    "start_h3": start_cell,
                    "end_h3": end_cell,
                    "is_reference": is_reference,
                    "status": "ok",
                })
                coord_rows.extend(route_to_rows(behavior, route_name, path, graph))
                plotted_routes[behavior].append((path, graph, is_reference))

    endpoint_df = pd.DataFrame(endpoint_rows)
    coords_df = pd.DataFrame(coord_rows)

    OUTPUT_COORDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    endpoint_df.to_csv(OUTPUT_ENDPOINTS_PATH, index=False)
    coords_df.to_csv(OUTPUT_COORDS_PATH, index=False)

    masked = env.loc[~env["has_wind_support"]].copy()
    map_env = env.loc[env["has_wind_support"], ["h3_cell", "lon", "lat", "u10", "v10", "chlor_a"]].copy()
    northward_support = map_env["v10"]
    map_env["w_cost"] = 100.0 * np.abs(northward_support - np.nanpercentile(northward_support.to_numpy(), 99)) / np.nanpercentile(np.abs(northward_support - np.nanpercentile(northward_support.to_numpy(), 99)), 99)
    map_env["c_cost"] = 100.0 * np.abs(map_env["u10"]) / np.nanpercentile(np.abs(map_env["u10"]).to_numpy(), 99)
    northward_distance_lookup = df.groupby("source_h3", as_index=False)["d_cost"].first()
    map_env = map_env.merge(northward_distance_lookup, left_on="h3_cell", right_on="source_h3", how="left")
    positive_floor = map_env.loc[map_env["chlor_a"] > 0, "chlor_a"].min()
    map_env["f_cost"] = 100.0 * np.abs(np.where(np.log(map_env["chlor_a"].clip(lower=positive_floor)) <= -1, np.log(map_env["chlor_a"].clip(lower=positive_floor)), -1) + 1) / np.nanpercentile(np.abs(np.where(np.log(map_env["chlor_a"].clip(lower=positive_floor)) <= -1, np.log(map_env["chlor_a"].clip(lower=positive_floor)), -1) + 1), 99)
    shared_overlay_max = float(np.nanpercentile(map_env[["w_cost", "c_cost", "d_cost", "f_cost"]].to_numpy(), 99))

    background_cols = {
        "support_only": ("w_cost", "Support cost background with endpoint sensitivity"),
        "crosswind_only": ("c_cost", "Crosswind cost background with endpoint sensitivity"),
        "distance_only": ("d_cost", "Distance cost background with endpoint sensitivity"),
        "food_only": ("f_cost", "Food cost background with endpoint sensitivity"),
    }

    fig, axes = plt.subplots(2, 2, figsize=(11, 13), constrained_layout=True)
    for ax, behavior in zip(axes.ravel(), ["support_only", "crosswind_only", "distance_only", "food_only"]):
        value_col, title = background_cols[behavior]
        sc = draw_component_map_panel(ax, map_env, value_col, masked, title, 0.0, shared_overlay_max)
        for path, graph, is_reference in plotted_routes[behavior]:
            first = graph[path[0]][path[1]]
            lons = [first["source_lon"]] + [graph[u][v]["target_lon"] for u, v in zip(path[:-1], path[1:])]
            lats = [first["source_lat"]] + [graph[u][v]["target_lat"] for u, v in zip(path[:-1], path[1:])]
            ax.plot(lons, lats, color=("crimson" if is_reference else "#7a7a7a"), linewidth=(2.2 if is_reference else 0.9), alpha=(1.0 if is_reference else 0.55))
        cbar = fig.colorbar(sc, ax=ax)
        cbar.set_label(f"Standardized cost (SCU), shared scale 0 to {shared_overlay_max:.1f}")
    fig.savefig(FIGURE_PATH, dpi=170)
    plt.close(fig)

    n_success = int((endpoint_df["status"] == "ok").sum())
    report = f'''# Endpoint sensitivity for Svalbard spring

## Question
How sensitive are the four current extreme-behavior routes to small changes in start and end H3 cells around the reference validation endpoints?

## Setup
- reference start cell: `{REFERENCE_START}`
- reference end cell: `{REFERENCE_END}`
- tested behaviors: `support_only`, `crosswind_only`, `distance_only`, `food_only`
- tested start cells: reference cell plus its H3 k=1 neighborhood
- tested end cells: reference cell plus its H3 k=1 neighborhood
- output route table kept intentionally compact, with coordinates only

## Outputs
- route coordinates: `results/tables/13_svalbard_endpoint_sensitivity_coordinates.csv`
- tested endpoint pairs: `results/tables/13_svalbard_endpoint_sensitivity_endpoints.csv`
- overlay figure: `results/figures/13_svalbard_endpoint_sensitivity_routes.png`

## Quick-look figure

![Endpoint sensitivity over four background cost maps](../figures/13_svalbard_endpoint_sensitivity_routes.png)

## Map styling
- reference least-cost path shown in **red**
- alternative endpoint-sensitivity routes shown in **grey**
- backgrounds use the usual four component cost maps for direct comparison

## Run summary
- successful routes across all tested behavior-endpoint combinations: **{n_success}**
'''
    REPORT_PATH.write_text(report)

    print("Ran Svalbard endpoint sensitivity experiment")
    print(f"successful routes: {n_success}")
    print(f"report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
