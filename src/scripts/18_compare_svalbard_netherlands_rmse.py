#!/usr/bin/env python3
"""
Compare saved Svalbard spring and Netherlands spring RMSE results and top-route
structures without rerunning any route simulations.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TABLE_DIR = PROJECT_ROOT / "results" / "tables"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"
REPORT_DIR = PROJECT_ROOT / "results" / "reports"

SVALBARD_RMSE = TABLE_DIR / "16_svalbard_full_bounded_rmse.csv"
NETHERLANDS_RMSE = TABLE_DIR / "16_netherlands_full_bounded_rmse.csv"
SVALBARD_BAND = TABLE_DIR / "17_svalbard_top20_band_error_summary.csv"
NETHERLANDS_BAND = TABLE_DIR / "17_netherlands_top20_band_error_summary.csv"
SVALBARD_TOP20 = TABLE_DIR / "17_svalbard_top20_rmse_behaviors.csv"
NETHERLANDS_TOP20 = TABLE_DIR / "17_netherlands_top20_rmse_behaviors.csv"

OUTPUT_SUMMARY = TABLE_DIR / "18_svalbard_netherlands_comparison_summary.csv"
FIGURE_RMSE = FIGURE_DIR / "18_svalbard_netherlands_best_rmse.png"
FIGURE_COEFF = FIGURE_DIR / "18_svalbard_netherlands_top20_coefficients.png"
FIGURE_BAND = FIGURE_DIR / "18_svalbard_netherlands_band_errors.png"
REPORT_PATH = REPORT_DIR / "18_compare-svalbard-netherlands-spring-rmse.md"


def coefficient_summary(df: pd.DataFrame, label: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "population": [label] * 4,
            "coefficient": ["a_wind", "b_crosswind", "c_distance", "d_food"],
            "min": [df["a_wind"].min(), df["b_crosswind"].min(), df["c_distance"].min(), df["d_food"].min()],
            "median": [df["a_wind"].median(), df["b_crosswind"].median(), df["c_distance"].median(), df["d_food"].median()],
            "max": [df["a_wind"].max(), df["b_crosswind"].max(), df["c_distance"].max(), df["d_food"].max()],
        }
    )


def main() -> None:
    svalbard_rmse = pd.read_csv(SVALBARD_RMSE)
    nl_rmse = pd.read_csv(NETHERLANDS_RMSE)
    svalbard_band = pd.read_csv(SVALBARD_BAND)
    nl_band = pd.read_csv(NETHERLANDS_BAND)
    svalbard_top20 = pd.read_csv(SVALBARD_TOP20)
    nl_top20 = pd.read_csv(NETHERLANDS_TOP20)

    svalbard_best = svalbard_rmse.iloc[0]
    nl_best = nl_rmse.iloc[0]

    summary_df = pd.DataFrame(
        [
            {
                "population": "svalbard_spring",
                "best_behavior": svalbard_best["behavior"],
                "best_rmse_km": svalbard_best["rmse_km"],
                "n_compared_bands": svalbard_best["n_compared_bands"],
                "a_wind": svalbard_best["a_wind"],
                "b_crosswind": svalbard_best["b_crosswind"],
                "c_distance": svalbard_best["c_distance"],
                "d_food": svalbard_best["d_food"],
            },
            {
                "population": "netherlands_spring",
                "best_behavior": nl_best["behavior"],
                "best_rmse_km": nl_best["rmse_km"],
                "n_compared_bands": nl_best["n_compared_bands"],
                "a_wind": nl_best["a_wind"],
                "b_crosswind": nl_best["b_crosswind"],
                "c_distance": nl_best["c_distance"],
                "d_food": nl_best["d_food"],
            },
        ]
    )

    coeff_df = pd.concat(
        [
            coefficient_summary(svalbard_top20, "Svalbard spring"),
            coefficient_summary(nl_top20, "Netherlands spring"),
        ],
        ignore_index=True,
    )

    OUTPUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    FIGURE_RMSE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    summary_df.to_csv(OUTPUT_SUMMARY, index=False)

    fig, ax = plt.subplots(figsize=(6.2, 4.8), constrained_layout=True)
    ax.bar(summary_df["population"], summary_df["best_rmse_km"], color=["#4c78a8", "#f58518"])
    ax.set_ylabel("Best RMSE (km)")
    ax.set_title("Best-route RMSE, Svalbard versus Netherlands spring")
    fig.savefig(FIGURE_RMSE, dpi=170)
    plt.close(fig)

    labels = ["a_wind", "b_crosswind", "c_distance", "d_food"]
    x = np.arange(len(labels))
    width = 0.35
    svalbard_medians = coeff_df.loc[coeff_df["population"] == "Svalbard spring", "median"].to_numpy()
    nl_medians = coeff_df.loc[coeff_df["population"] == "Netherlands spring", "median"].to_numpy()

    fig, ax = plt.subplots(figsize=(7.4, 5.2), constrained_layout=True)
    ax.bar(x - width / 2, svalbard_medians, width, label="Svalbard spring", color="#4c78a8")
    ax.bar(x + width / 2, nl_medians, width, label="Netherlands spring", color="#f58518")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Median coefficient among top 20")
    ax.set_title("Top-20 coefficient medians by population")
    ax.legend()
    fig.savefig(FIGURE_COEFF, dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.6, 6.2), constrained_layout=True)
    ax.plot(svalbard_band["mean_abs_lon_error_km"], svalbard_band["benchmark_lat_median"], color="#4c78a8", linewidth=2.5, label="Svalbard spring")
    ax.plot(nl_band["mean_abs_lon_error_km"], nl_band["benchmark_lat_median"], color="#f58518", linewidth=2.5, label="Netherlands spring")
    ax.set_xlabel("Mean absolute longitude error (km)")
    ax.set_ylabel("Latitude (degrees)")
    ax.set_title("Top-20 latitude-band errors by population")
    ax.legend()
    fig.savefig(FIGURE_BAND, dpi=170)
    plt.close(fig)

    svalbard_w = coeff_df.loc[(coeff_df["population"] == "Svalbard spring") & (coeff_df["coefficient"] == "a_wind"), "median"].iloc[0]
    nl_w = coeff_df.loc[(coeff_df["population"] == "Netherlands spring") & (coeff_df["coefficient"] == "a_wind"), "median"].iloc[0]
    svalbard_d = coeff_df.loc[(coeff_df["population"] == "Svalbard spring") & (coeff_df["coefficient"] == "c_distance"), "median"].iloc[0]
    nl_d = coeff_df.loc[(coeff_df["population"] == "Netherlands spring") & (coeff_df["coefficient"] == "c_distance"), "median"].iloc[0]

    report = f'''# Compare Svalbard spring and Netherlands spring RMSE results

## Question
Do the Svalbard spring and Netherlands spring H3 route experiments favor similar or different behavioral weight structures when ranked by RMSE against their benchmark flyways?

## Inputs
- `results/tables/16_svalbard_full_bounded_rmse.csv`
- `results/tables/16_netherlands_full_bounded_rmse.csv`
- `results/tables/17_svalbard_top20_rmse_behaviors.csv`
- `results/tables/17_netherlands_top20_rmse_behaviors.csv`
- `results/tables/17_svalbard_top20_band_error_summary.csv`
- `results/tables/17_netherlands_top20_band_error_summary.csv`

## Outputs
- comparison summary table: `results/tables/18_svalbard_netherlands_comparison_summary.csv`
- best-RMSE figure: `results/figures/18_svalbard_netherlands_best_rmse.png`
- coefficient comparison figure: `results/figures/18_svalbard_netherlands_top20_coefficients.png`
- band-error comparison figure: `results/figures/18_svalbard_netherlands_band_errors.png`

## Quick-look figures

![Best RMSE comparison](../figures/18_svalbard_netherlands_best_rmse.png)

![Coefficient median comparison](../figures/18_svalbard_netherlands_top20_coefficients.png)

![Latitude-band error comparison](../figures/18_svalbard_netherlands_band_errors.png)

## Best-route comparison
- **Svalbard spring**
  - best behavior: **{svalbard_best['behavior']}**
  - best RMSE: **{svalbard_best['rmse_km']:.1f} km**
  - weights: **({svalbard_best['a_wind']:.1f}, {svalbard_best['b_crosswind']:.1f}, {svalbard_best['c_distance']:.1f}, {svalbard_best['d_food']:.1f})**
- **Netherlands spring**
  - best behavior: **{nl_best['behavior']}**
  - best RMSE: **{nl_best['rmse_km']:.1f} km**
  - weights: **({nl_best['a_wind']:.1f}, {nl_best['b_crosswind']:.1f}, {nl_best['c_distance']:.1f}, {nl_best['d_food']:.1f})**

## Top-20 coefficient comparison
- Svalbard top-20 median wind weight: **{svalbard_w:.1f}**
- Netherlands top-20 median wind weight: **{nl_w:.1f}**
- Svalbard top-20 median distance weight: **{svalbard_d:.1f}**
- Netherlands top-20 median distance weight: **{nl_d:.1f}**

## Interpretation
The two populations do not point to exactly the same coefficient regime. Svalbard spring is more strongly wind-dominant among its top-RMSE solutions, whereas Netherlands spring places relatively more weight on distance alongside wind.

That is already scientifically useful, because it suggests the H3 routing framework may be flexible enough to express population-specific movement regimes rather than collapsing to one generic optimum across cases.

The RMSE comparison also suggests that Netherlands spring is reproduced somewhat more closely under the current setup than Svalbard spring, at least by this latitude-binned benchmark metric. That does not automatically mean the Netherlands case is biologically simpler, but it does mean the current graph-plus-endpoint setup aligns more closely with that benchmark summary.

The latitude-band comparison figure should be used to see whether the two populations struggle in the same parts of the flyway or in different latitude zones. If the difficult bands differ, that points toward case-specific route mismatches rather than one uniform model defect.

## Efficiency note
This comparison uses saved outputs only. It does not rerun route sweeps, endpoint sensitivity experiments, or mixed-behavior batches.
'''
    REPORT_PATH.write_text(report)

    print("Compared Svalbard spring and Netherlands spring RMSE outputs")
    print(f"Svalbard best RMSE: {svalbard_best['rmse_km']:.1f} km")
    print(f"Netherlands best RMSE: {nl_best['rmse_km']:.1f} km")
    print(f"report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
