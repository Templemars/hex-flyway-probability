from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


def nearest_h3_cell(env: pd.DataFrame, lon: float, lat: float) -> str:
    distance = (env["lon"] - lon) ** 2 + (env["lat"] - lat) ** 2
    return str(env.loc[distance.idxmin(), "h3_cell"])


def derive_prototype_endpoints(
    benchmark: pd.DataFrame,
    env: pd.DataFrame,
    start_rule: str,
    end_rule: str,
) -> tuple[dict, dict]:
    start_point = benchmark.iloc[0]
    end_point = benchmark.iloc[-1]
    start_lon = float(start_point["lon_median10"])
    start_lat = float(start_point["lat_median10"])
    end_lon = float(end_point["lon_median10"])
    end_lat = float(end_point["lat_median10"])
    return (
        {
            "endpoint_role": "start",
            "benchmark_rule": start_rule,
            "lon": start_lon,
            "lat": start_lat,
            "nearest_h3_cell": nearest_h3_cell(env, start_lon, start_lat),
        },
        {
            "endpoint_role": "end",
            "benchmark_rule": end_rule,
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
            edge_distance_km=float(getattr(row, "edge_distance_km", np.nan)),
            w_cost=float(getattr(row, "w_cost", np.nan)),
            c_cost=float(getattr(row, "c_cost", np.nan)),
            d_cost=float(getattr(row, "d_cost", np.nan)),
            f_cost=float(getattr(row, "f_cost", np.nan)),
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
        total_distance += edge.get("edge_distance_km", 0.0)
        total_w += edge.get("w_cost", 0.0)
        total_c += edge.get("c_cost", 0.0)
        total_d += edge.get("d_cost", 0.0)
        total_f += edge.get("f_cost", 0.0)
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
                "edge_distance_km": edge.get("edge_distance_km", np.nan),
                "w_cost": edge.get("w_cost", np.nan),
                "c_cost": edge.get("c_cost", np.nan),
                "d_cost": edge.get("d_cost", np.nan),
                "f_cost": edge.get("f_cost", np.nan),
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


def assign_lat_band(lat: pd.Series) -> pd.Series:
    edges = np.arange(-80, 71, 10)
    labels = [f"({lo}, {hi}]" for lo, hi in zip(edges[:-1], edges[1:])]
    return pd.cut(lat, bins=edges, labels=labels, include_lowest=False, right=True)


def route_points_from_group(route: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "lon": [route.iloc[0]["source_lon"]] + route["target_lon"].tolist(),
            "lat": [route.iloc[0]["source_lat"]] + route["target_lat"].tolist(),
        }
    )


def draw_component_map_panel(ax, df, value_col, masked_df, title, vmin, vmax):
    ax.scatter(masked_df["lon"], masked_df["lat"], s=75, marker="h", color="#c8b08f", alpha=0.55, linewidths=0)
    sc = ax.scatter(df["lon"], df["lat"], c=df[value_col], s=65, marker="h", cmap="viridis", linewidths=0, alpha=0.9, vmin=vmin, vmax=vmax)
    ax.set_title(title)
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_xlim(-95, 35)
    ax.set_ylim(-80, 85)
    return sc
