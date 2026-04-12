#!/usr/bin/env python3
"""
Render the Svalbard endpoint-sensitivity figure and report from saved outputs only.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from flyway_h3.workflow_utils import draw_component_map_panel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COORDS_PATH = PROJECT_ROOT / "results" / "tables" / "13_svalbard_endpoint_sensitivity_coordinates.csv"
ENDPOINTS_PATH = PROJECT_ROOT / "results" / "tables" / "13_svalbard_endpoint_sensitivity_endpoints.csv"
METRICS_PATH = PROJECT_ROOT / "results" / "tables" / "13_svalbard_endpoint_sensitivity_similarity.csv"
ENV_PATH = PROJECT_ROOT / "data" / "processed" / "grids" / "h3_environment_res3.csv"
FIGURE_PATH = PROJECT_ROOT / "results" / "figures" / "13_svalbard_endpoint_sensitivity_routes.png"
REPORT_PATH = PROJECT_ROOT / "results" / "reports" / "13_endpoint-sensitivity-svalbard.md"

REFERENCE_START = "83eea8fffffffff"
REFERENCE_END = "83076bfffffffff"
RANDOM_SEED = 42


def main() -> None:
    coords_df = pd.read_csv(COORDS_PATH)
    endpoint_df = pd.read_csv(ENDPOINTS_PATH)
    metrics_df = pd.read_csv(METRICS_PATH)
    env = pd.read_csv(ENV_PATH)

    env["has_wind_support"] = ~(env[["u10", "v10"]].isna().all(axis=1))
    masked = env.loc[~env["has_wind_support"]].copy()
    map_env = env.loc[env["has_wind_support"], ["h3_cell", "lon", "lat", "u10", "v10", "chlor_a"]].copy()
    northward_support = map_env["v10"]
    positive_floor = map_env.loc[map_env["chlor_a"] > 0, "chlor_a"].min()
    map_env["w_cost"] = 100.0 * np.abs(northward_support - np.nanpercentile(northward_support.to_numpy(), 99)) / np.nanpercentile(np.abs(northward_support - np.nanpercentile(northward_support.to_numpy(), 99)), 99)
    map_env["c_cost"] = 100.0 * np.abs(map_env["u10"]) / np.nanpercentile(np.abs(map_env["u10"]).to_numpy(), 99)
    map_env["d_cost"] = float(np.nanmedian(map_env["u10"].abs()))
    map_env["f_cost"] = 100.0 * np.abs(np.where(np.log(map_env["chlor_a"].clip(lower=positive_floor)) <= -1, np.log(map_env["chlor_a"].clip(lower=positive_floor)), -1) + 1) / np.nanpercentile(np.abs(np.where(np.log(map_env["chlor_a"].clip(lower=positive_floor)) <= -1, np.log(map_env["chlor_a"].clip(lower=positive_floor)), -1) + 1), 99)
    shared_overlay_max = float(np.nanpercentile(map_env[["w_cost", "c_cost", "d_cost", "f_cost"]].to_numpy(), 99))

    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

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
        subset = coords_df.loc[coords_df["behavior"] == behavior].copy()
        for route_name, route in subset.groupby("route_name"):
            color = "crimson" if route_name == f"start_{REFERENCE_START}_end_{REFERENCE_END}" else "#7a7a7a"
            linewidth = 2.2 if color == "crimson" else 0.9
            alpha = 1.0 if color == "crimson" else 0.55
            ax.plot(route["lon"], route["lat"], color=color, linewidth=linewidth, alpha=alpha)
        cbar = fig.colorbar(sc, ax=ax)
        cbar.set_label(f"Standardized cost (SCU), shared scale 0 to {shared_overlay_max:.1f}")
    fig.savefig(FIGURE_PATH, dpi=170)
    plt.close(fig)

    n_success = int((endpoint_df["status"] == "ok").sum()) if not endpoint_df.empty else 0
    behavior_summary = []
    if not metrics_df.empty:
        non_reference = metrics_df.loc[~metrics_df["is_reference"]].copy()
        if not non_reference.empty:
            summary = non_reference.groupby("behavior")[["mean_nearest_km", "p95_nearest_km", "fraction_within_1step"]].mean().reset_index()
            for row in summary.itertuples(index=False):
                behavior_summary.append(f"- `{row.behavior}`: mean nearest-route distance ≈ **{row.mean_nearest_km:.1f} km**, mean P95 distance ≈ **{row.p95_nearest_km:.1f} km**, mean fraction within 1 H3 step ≈ **{row.fraction_within_1step:.2f}**")
    report = f'''# Endpoint sensitivity for Svalbard spring

## Question
How sensitive are the four current extreme-behavior routes to small changes in start and end H3 cells around the reference validation endpoints?

## Outputs
- route coordinates: `results/tables/13_svalbard_endpoint_sensitivity_coordinates.csv`
- tested endpoint pairs: `results/tables/13_svalbard_endpoint_sensitivity_endpoints.csv`
- route-to-reference similarity metrics: `results/tables/13_svalbard_endpoint_sensitivity_similarity.csv`
- overlay figure: `results/figures/13_svalbard_endpoint_sensitivity_routes.png`

## Quick-look figure

![Endpoint sensitivity over four background cost maps](../figures/13_svalbard_endpoint_sensitivity_routes.png)

## Run summary
- successful routes across all tested behavior-endpoint combinations: **{n_success}**
- random seed: **{RANDOM_SEED}**

## Behavior-level averages across non-reference routes
{chr(10).join(behavior_summary) if behavior_summary else '- similarity summary not available'}

## Efficiency note
This reporting step reuses saved endpoint-sensitivity outputs and does not rerun the sensitivity routes.
'''
    REPORT_PATH.write_text(report)
    print("Rendered Svalbard step-13 report from saved outputs")


if __name__ == "__main__":
    main()
