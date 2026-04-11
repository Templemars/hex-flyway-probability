# Compute H3 cost components

## Question
What do the raw and standardized movement-cost components look like on the directed H3 graph, and do they correctly preserve the published food-cost logic?

## Input data
- `data/processed/grids/h3_edge_environment_res3.csv`
- `data/processed/grids/h3_environment_res3.csv`

## Audit result: food-cost correction
The first implementation needed one important correction.

The paper logic implies:
- low chlorophyll should produce high food cost
- high chlorophyll should produce low food cost
- cells above the productivity threshold should collapse toward the same low-cost class

The original implementation preserved that direction for positive chlorophyll values, but treated zero chlorophyll as missing after the log transform. That was not acceptable, because zero-food cells should behave like very poor food cells, not drop out.

The corrected implementation now:
- replaces non-positive chlorophyll with a small positive floor before taking the log
- uses the smallest positive chlorophyll value in the H3 environmental table as that floor
- therefore keeps zero-chlorophyll cells in the cost surface as high-cost cells

Audit values:
- zero or non-positive chlorophyll cells in H3 table: **1869**
- positive chlorophyll floor used for the log transform: **0.02446900**

## Method
- compute directional edge costs for parallel wind, crosswind, true distance, and food
- standardize each component with the agreed P99-based scaling philosophy
- additionally produce four cell-level component maps for transparency
- for the two wind component maps, assume a bird flying in a straight northward direction everywhere
- for the distance map, assign to each cell the true distance of the outgoing edge whose bearing is closest to north

## Key formulas used
- movement direction comes from the edge bearing for the edge-level table
- wind support is the projection of the source wind vector onto the movement direction
- raw parallel wind cost = distance from `P99(windsupport)`
- raw crosswind cost = magnitude of the wind component perpendicular to movement
- raw distance cost = true H3 edge distance in km for the edge table
- diagnostic distance map = true distance of the outgoing edge whose bearing is closest to north, one value per source cell
- raw food cost = `|log(chla) + 1|` after capping high-productivity cells and flooring non-positive chlorophyll values for numerical stability
- standardized component cost = `100 * raw_component / P99(raw_component)`

## Outputs
- component table: `data/processed/grids/h3_edge_cost_components_res3.csv`
- summary table: `results/tables/11_compute_h3_cost_components_summary.csv`
- example rows: `results/tables/11_compute_h3_cost_components_example_rows.csv`
- figures:
  - `results/figures/11_raw_component_histograms.png`
  - `results/figures/11_standardized_component_histograms.png`
  - `results/figures/11_wind_vs_crosswind_scatter.png`
  - `results/figures/11_map_parallel_wind_cost_northward.png`
  - `results/figures/11_map_crosswind_cost_northward.png`
  - `results/figures/11_map_distance_cost.png`
  - `results/figures/11_map_food_cost.png`

## Quick-look figures

![Raw component histograms](../figures/11_raw_component_histograms.png)

![Standardized component histograms](../figures/11_standardized_component_histograms.png)

![Wind vs crosswind standardized costs](../figures/11_wind_vs_crosswind_scatter.png)

![Parallel wind cost map](../figures/11_map_parallel_wind_cost_northward.png)

![Crosswind cost map](../figures/11_map_crosswind_cost_northward.png)

![Distance cost map](../figures/11_map_distance_cost.png)

![Food cost map](../figures/11_map_food_cost.png)

## Interpretation
This step now does what it should scientifically: it creates an explicit directional cost graph while keeping the food surface behavior consistent with the published logic that poor-food cells must be expensive.

The four maps are also useful because they separate two different views of the model:
- edge-level directional costs used in the real path calculations
- cell-level component surfaces used for intuitive inspection

For the wind maps, the northward-flight assumption is only for visualizing the directional wind components as a global surface. The real graph still uses each actual edge bearing.
For the distance map, each cell is assigned the true distance of its outgoing edge closest to north. This is also diagnostic rather than part of the routing graph itself, but it is a real edge quantity rather than an artificial cumulative construction.

## Points to watch
- the distance component in the routing model still represents true H3 edge length, which is an intentional refinement relative to the legacy constant-per-step distance term
- the mapped northward distance surface is a separate diagnostic layer for interpretability, based on a real outgoing northward edge per cell
- the legacy constant distance reference extracted from the standardized wind term is **49.999**, which provides a direct bridge back to the earlier formulation
- the visual wind maps are diagnostic surfaces, not replacements for the directional edge-level calculations

## Next step
Combine these standardized components using selected weight sets and run the first Dijkstra path calculation for the H3 graph.
