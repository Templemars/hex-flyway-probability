# Run mixed-behavior H3 Dijkstra batch

## Question
What happens when a small explicit mixed-behavior set is run for the Svalbard spring H3 prototype, using the current validation-linked endpoints and the ERA5-supported routing mask?

## Input data
- `data/processed/grids/h3_edge_cost_components_res3.csv`
- `data/processed/grids/h3_environment_res3.csv`
- `data/raw/benchmark_from_2025/gdf_SS_10.csv`

## Mixed behaviors used
Coefficient order:
- `a = wind support`
- `b = crosswind`
- `c = distance`
- `d = food`

The tested mixed behaviors are:
- `wind_distance_balanced = (0.5, 0.0, 0.5, 0.0)`
- `wind_food_balanced = (0.5, 0.0, 0.0, 0.5)`
- `wind_crosswind_distance = (0.4, 0.3, 0.3, 0.0)`
- `wind_crosswind_food = (0.4, 0.3, 0.0, 0.3)`
- `balanced_all_four = (0.25, 0.25, 0.25, 0.25)`
- `wind_dominant_with_food = (0.5, 0.2, 0.0, 0.3)`

These were chosen as a small interpretable set rather than a full coefficient sweep.

See:
- `results/tables/14_svalbard_mixed_dijkstra_weight_sets.csv`

## Endpoint rule used
- start point = first row of `gdf_SS_10.csv`
- end point = last row of `gdf_SS_10.csv`
- both matched to nearest H3 cells

See:
- `results/tables/14_svalbard_mixed_dijkstra_endpoints.csv`

## Outputs
- path table: `results/tables/14_svalbard_mixed_dijkstra_paths.csv`
- route summary table: `results/tables/14_svalbard_mixed_dijkstra_summary.csv`
- failed-behavior table when relevant: `results/tables/14_svalbard_mixed_dijkstra_failures.csv`
- weight table: `results/tables/14_svalbard_mixed_dijkstra_weight_sets.csv`
- endpoint table: `results/tables/14_svalbard_mixed_dijkstra_endpoints.csv`
- route figure: `results/figures/14_svalbard_mixed_dijkstra_routes.png`
- diagnostic overlay figure: `results/figures/14_mixed_component_maps_with_lcps.png`

## Quick-look figures

![Mixed-behavior H3 Dijkstra routes](../figures/14_svalbard_mixed_dijkstra_routes.png)

![Mixed-behavior diagnostic overlays](../figures/14_mixed_component_maps_with_lcps.png)

## Run summary
- number of tested mixed behaviors: **6**
- number of successful route runs: **6**
- number of failed route runs: **0**

## Interpretation
This is the first step beyond the diagnostic extreme single-factor routes. That matters because mixed behaviors are much closer to the actual modeling goal than pure one-component optimizers.

The current batch is intentionally small and interpretable. It is meant to show whether adding modest combinations of wind, crosswind, distance, and food produces route families that look more coherent and biologically plausible than the extreme cases, while still remaining easy to reason about.

The most important things to inspect are:
- whether the mixed routes collapse toward a common corridor or remain strongly separated
- whether adding food shifts routes in a visibly different way from adding distance
- whether crosswind-containing mixtures create routes that are more dispersed or more structured
- whether the resulting paths look less extreme than the earlier single-factor routes

This remains a prototype stage rather than a final validation result. But it is a more meaningful biological step than the extreme-behavior batch, because it tests combinations that a real movement strategy is more likely to resemble.

## Next step
If these mixed routes look interpretable, the next stage should likely be either a slightly broader mixed-behavior set or the first explicit route-to-benchmark comparison metric for the Svalbard spring case.

Additional route summary:
- lowest total modeled path cost in this mixed batch: **wind_food_balanced**
- corresponding total cost: **3808.970**
- corresponding total distance: **19137.5 km**
- corresponding step count: **159**
