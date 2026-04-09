# Compute H3 cost components

## Question
What do the raw and standardized movement-cost components look like on the directed H3 graph?

## Input data
- `data/processed/grids/h3_edge_environment_res3.csv`

## Method
- compute directional movement geometry from the existing edge table
- compute raw component values for:
  - parallel wind cost
  - crosswind cost
  - true edge distance cost
  - food cost using the published chlorophyll treatment
- standardize components using the agreed P99-based scaling philosophy
- retain the legacy constant distance reference from the old paper as a comparison point

## Key formulas used
- movement direction comes from the edge bearing
- wind support is the projection of the source wind vector onto the movement direction
- raw parallel wind cost = distance from `P99(windsupport)`
- raw crosswind cost = magnitude of the wind component perpendicular to movement
- raw distance cost = true H3 edge distance in km
- raw food cost follows the published log-based chlorophyll transform
- standardized component cost = `100 * raw_component / P99(raw_component)`

## Outputs
- component table: `data/processed/grids/h3_edge_cost_components_res3.csv`
- summary table: `results/tables/11_compute_h3_cost_components_summary.csv`
- example rows: `results/tables/11_compute_h3_cost_components_example_rows.csv`
- figures:
  - `results/figures/11_raw_component_histograms.png`
  - `results/figures/11_standardized_component_histograms.png`
  - `results/figures/11_wind_vs_crosswind_scatter.png`

## Quick-look figures

![Raw component histograms](../figures/11_raw_component_histograms.png)

![Standardized component histograms](../figures/11_standardized_component_histograms.png)

![Wind vs crosswind standardized costs](../figures/11_wind_vs_crosswind_scatter.png)

## Interpretation
This is the first full cost-component table for the H3 sequel. At this point the model is no longer just a geometric graph; it is now an explicitly directional environmental cost graph. That is the core transition from project setup into the real movement model.

The structure is also scientifically useful because it lets us inspect each component independently before combining weights. That is important for transparency and for catching mistakes early.

## Points to watch
- the distance component now represents true H3 edge length, which is an intentional refinement relative to the legacy constant-per-step distance term
- the food component follows the published chlorophyll treatment, so comparisons to the 2025 paper remain interpretable
- the legacy constant distance reference extracted from the standardized wind term is **49.999**, which provides a direct bridge back to the earlier formulation

## Next step
Combine these standardized components using selected weight sets and run the first Dijkstra path calculation for the H3 graph.
