#!/usr/bin/env python3
"""
Run the full bounded H3 Dijkstra behavior sweep for a chosen benchmark population.

Reuses the saved spring H3 graph inputs and cost-component tables. Only the
population-specific benchmark summary and output prefixes change.
"""

from __future__ import annotations

import sys
from itertools import product
from pathlib import Path

import networkx as nx
import pandas as pd

from flyway_h3.workflow_utils import (
    build_graph,
    derive_prototype_endpoints,
    nearest_h3_cell,
    summarize_path,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPONENT_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_edge_cost_components_res3.csv"
ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_environment_res3.csv"
BENCHMARK_DIR = PROJECT_ROOT / "data" / "raw" / "benchmark_from_2025"
RESULTS_TABLE_DIR = PROJECT_ROOT / "results" / "tables"

POPULATION_MAP = {
    "svalbard_spring": {
        "benchmark_path": BENCHMARK_DIR / "gdf_SS_10.csv",
        "prefix": "15_svalbard_full_bounded_dijkstra",
        "start_rule": "first_row_of_gdf_SS_10",
        "end_rule": "last_row_of_gdf_SS_10",
    },
    "netherlands_spring": {
        "benchmark_path": BENCHMARK_DIR / "gdf_NS_10.csv",
        "prefix": "15_netherlands_full_bounded_dijkstra",
        "start_rule": "first_row_of_gdf_NS_10",
        "end_rule": "last_row_of_gdf_NS_10",
    },
}


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


def main() -> None:
    population_key = sys.argv[1] if len(sys.argv) > 1 else "svalbard_spring"
    if population_key not in POPULATION_MAP:
        raise SystemExit(f"Unknown population '{population_key}'. Choose from: {', '.join(sorted(POPULATION_MAP))}")

    cfg = POPULATION_MAP[population_key]
    prefix = cfg["prefix"]
    output_route_path = RESULTS_TABLE_DIR / f"{prefix}_paths.csv"
    output_summary_path = RESULTS_TABLE_DIR / f"{prefix}_summary.csv"
    output_weights_path = RESULTS_TABLE_DIR / f"{prefix}_weight_sets.csv"
    output_endpoints_path = RESULTS_TABLE_DIR / f"{prefix}_endpoints.csv"
    failed_path = RESULTS_TABLE_DIR / f"{prefix}_failures.csv"

    weight_sets = generate_weight_sets()
    df = pd.read_csv(COMPONENT_PATH)
    env = pd.read_csv(ENV_PATH)
    benchmark = pd.read_csv(cfg["benchmark_path"])

    env["has_wind_support"] = ~(env[["u10", "v10"]].isna().all(axis=1))
    water_cells = set(env.loc[env["has_wind_support"], "h3_cell"].astype(str))
    df = df[df["source_h3"].astype(str).isin(water_cells) & df["target_h3"].astype(str).isin(water_cells)].copy()

    start_record, end_record = derive_prototype_endpoints(benchmark, env, cfg["start_rule"], cfg["end_rule"])
    start_cell = start_record["nearest_h3_cell"]
    end_cell = end_record["nearest_h3_cell"]

    weights_df = pd.DataFrame(weight_sets, columns=["behavior", "a_wind", "b_crosswind", "c_distance", "d_food"])
    endpoints_df = pd.DataFrame([start_record, end_record])

    all_path_rows = []
    summaries = []
    failed_behaviors = []

    n_total = len(weight_sets)
    for idx, (behavior, a, b, c, d) in enumerate(weight_sets, start=1):
        if idx == 1 or idx % 10 == 0 or idx == n_total:
            print(
                f"[{population_key}] behavior {idx}/{n_total}: {behavior} "
                f"weights=({a:.1f}, {b:.1f}, {c:.1f}, {d:.1f})",
                flush=True,
            )
        run_df = df.copy()
        run_df["total_cost"] = a * run_df["w_cost"] + b * run_df["c_cost"] + c * run_df["d_cost"] + d * run_df["f_cost"]
        graph = build_graph(run_df, "total_cost")
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
            print(f"[{population_key}] failed: {behavior} ({type(exc).__name__}: {exc})", flush=True)
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

    output_route_path.parent.mkdir(parents=True, exist_ok=True)
    path_df.to_csv(output_route_path, index=False)
    summary_df.to_csv(output_summary_path, index=False)
    weights_df.to_csv(output_weights_path, index=False)
    endpoints_df.to_csv(output_endpoints_path, index=False)
    if not failed_df.empty:
        failed_df.to_csv(failed_path, index=False)

    print(f"Ran full bounded H3 Dijkstra sweep for {population_key}")
    print(f"tested behaviors: {len(weights_df)}")
    print(f"successful routes: {0 if summary_df.empty else len(summary_df)}")
    print(f"failed routes: {0 if failed_df.empty else len(failed_df)}")
    print(f"paths: {output_route_path}")
    print(f"summary: {output_summary_path}")


if __name__ == "__main__":
    main()
