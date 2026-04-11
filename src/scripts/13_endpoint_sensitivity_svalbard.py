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
BEHAVIOR = "food_only"
WEIGHTS = {"w_cost": 0.0, "c_cost": 0.0, "d_cost": 0.0, "f_cost": 1.0}


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


def route_to_rows(route_name: str, path: list[str], graph: nx.DiGraph) -> list[dict]:
    rows = []
    if len(path) < 2:
        return rows
    first = graph[path[0]][path[1]]
    rows.append({"route_name": route_name, "point_index": 0, "lon": first["source_lon"], "lat": first["source_lat"]})
    for i, (u, v) in enumerate(zip(path[:-1], path[1:]), start=1):
        edge = graph[u][v]
        rows.append({"route_name": route_name, "point_index": i, "lon": edge["target_lon"], "lat": edge["target_lat"]})
    return rows


def main() -> None:
    df = pd.read_csv(COMPONENT_PATH)
    env = pd.read_csv(ENV_PATH)
    env["has_wind_support"] = ~(env[["u10", "v10"]].isna().all(axis=1))
    water_cells = set(env.loc[env["has_wind_support"], "h3_cell"].astype(str))
    df = df[df["source_h3"].astype(str).isin(water_cells) & df["target_h3"].astype(str).isin(water_cells)].copy()
    df["total_cost"] = sum(weight * df[col] for col, weight in WEIGHTS.items())

    graph = build_graph(df)
    start_candidates = sorted(h3.grid_disk(REFERENCE_START, 1))
    end_candidates = sorted(h3.grid_disk(REFERENCE_END, 1))

    endpoint_rows = []
    coord_rows = []
    plotted_routes = []

    for start_cell in start_candidates:
        for end_cell in end_candidates:
            route_name = f"start_{start_cell}_end_{end_cell}"
            is_reference = start_cell == REFERENCE_START and end_cell == REFERENCE_END
            if start_cell not in graph or end_cell not in graph:
                endpoint_rows.append({
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
                    "route_name": route_name,
                    "start_h3": start_cell,
                    "end_h3": end_cell,
                    "is_reference": is_reference,
                    "status": type(exc).__name__,
                })
                continue

            endpoint_rows.append({
                "route_name": route_name,
                "start_h3": start_cell,
                "end_h3": end_cell,
                "is_reference": is_reference,
                "status": "ok",
            })
            coord_rows.extend(route_to_rows(route_name, path, graph))
            plotted_routes.append((route_name, path, is_reference))

    endpoint_df = pd.DataFrame(endpoint_rows)
    coords_df = pd.DataFrame(coord_rows)

    OUTPUT_COORDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    endpoint_df.to_csv(OUTPUT_ENDPOINTS_PATH, index=False)
    coords_df.to_csv(OUTPUT_COORDS_PATH, index=False)

    fig, ax = plt.subplots(figsize=(8.2, 10.5), constrained_layout=True)
    masked = env.loc[~env["has_wind_support"]].copy()
    supported = env.loc[env["has_wind_support"]].copy()
    ax.scatter(masked["lon"], masked["lat"], s=90, marker="h", color="#c8b08f", alpha=0.75, linewidths=0)
    ax.scatter(supported["lon"], supported["lat"], s=65, marker="h", color="#dceaf7", alpha=0.35, linewidths=0)

    for route_name, path, is_reference in plotted_routes:
        first = graph[path[0]][path[1]]
        lons = [first["source_lon"]] + [graph[u][v]["target_lon"] for u, v in zip(path[:-1], path[1:])]
        lats = [first["source_lat"]] + [graph[u][v]["target_lat"] for u, v in zip(path[:-1], path[1:])]
        ax.plot(lons, lats, color=("crimson" if is_reference else "#7a7a7a"), linewidth=(2.2 if is_reference else 1.0), alpha=(1.0 if is_reference else 0.65))

    ax.set_title("Svalbard endpoint sensitivity, food-only reference behavior")
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    fig.savefig(FIGURE_PATH, dpi=170)
    plt.close(fig)

    report = f'''# Endpoint sensitivity for Svalbard spring

## Question
How sensitive is the current Svalbard spring prototype to small changes in start and end H3 cells around the reference validation endpoints?

## Setup
- reference behavior: `{BEHAVIOR}`
- reference start cell: `{REFERENCE_START}`
- reference end cell: `{REFERENCE_END}`
- tested start cells: reference cell plus its H3 k=1 neighborhood
- tested end cells: reference cell plus its H3 k=1 neighborhood
- output route table kept intentionally compact, with coordinates only

## Outputs
- route coordinates: `results/tables/13_svalbard_endpoint_sensitivity_coordinates.csv`
- tested endpoint pairs: `results/tables/13_svalbard_endpoint_sensitivity_endpoints.csv`
- route figure: `results/figures/13_svalbard_endpoint_sensitivity_routes.png`

## Map styling
- reference least-cost path shown in **red**
- alternative endpoint-sensitivity routes shown in **grey**
'''
    REPORT_PATH.write_text(report)

    print("Ran Svalbard endpoint sensitivity experiment")
    print(f"successful routes: {(endpoint_df['status'] == 'ok').sum()}")
    print(f"reference route present: {bool(((endpoint_df['is_reference']) & (endpoint_df['status'] == 'ok')).any())}")
    print(f"report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
