# Run first H3 Dijkstra prototype

## Question
What do the first Svalbard spring Dijkstra routes look like across the agreed prototype behavior set?

## Input data
- `data/processed/grids/h3_edge_cost_components_res3.csv`
- `data/processed/grids/h3_environment_res3.csv`
- `data/raw/benchmark_from_2025/gdf_SS_10.csv`

## Behavior set used
This first extreme-behavior batch uses only four single-factor cases, with coefficient order:
- `a = wind support`
- `b = crosswind`
- `c = distance`
- `d = food`

The tested extreme behaviors are:
- support only
- crosswind only
- distance only
- food only

See:
- `results/tables/12_svalbard_dijkstra_weight_sets.csv`

## Routing mask used
Following the 2025 paper's overwater-routing stance, the first H3 prototype now uses the transferred benchmark ERA5 wind support as its routing-domain mask.

Implementation here:
- identify H3 cells that have valid transferred `u10` and `v10` values in the benchmark environmental table
- keep only edges whose source and target both lie inside that supported domain
- show supported versus masked cells distinctly on the global route map

Interpretation:
- this is a data-support mask derived from the benchmark ERA5 support
- for this prototype it is preferred over a separate polygon land mask because it matches the environmental support actually used in the cost construction

## Prototype endpoint rule used
This first Dijkstra test uses a temporary transparent endpoint rule rather than a claimed final biological endpoint definition.

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

## Quick-look figure

![First H3 Dijkstra prototype routes](../figures/12_svalbard_dijkstra_routes.png)

## First reading
- number of tested behaviors: **4**
- successful route runs: **4**
- failed route runs: **0**

## Interpretation
This is the first end-to-end H3 route prototype with an explicit ERA5-supported routing domain: standardized edge costs are now being turned into actual destination-constrained paths. That is a meaningful transition from cost construction into flyway simulation.

The current routes should still be treated as prototype behavior diagnostics, not final biological claims, because:
- the endpoint rule is still provisional
- the distance term remains under explicit caution
- the behavior set is a deliberately small exploratory subset

A scientifically important issue also emerged immediately: at least one behavior can fail under package Dijkstra even when the cost components are non-negative. If that happens, it should be treated as a modeling red flag, not hidden as a technical nuisance.

## Points to watch
- if some routes look implausibly grid-aligned, revisit the distance red flag
- if behavior differences are weak, the component scaling or endpoint rule may be suppressing contrast
- if behavior differences are extreme, inspect whether one component is dominating too strongly

## Next step
Inspect the route table and summaries carefully, then decide whether the first endpoint rule is good enough to keep for the next round or should already be refined.

Additional route summary:
- best current prototype by total cost: **food_only**
- best prototype total cost: **1292.521**
- best prototype total distance: **22714.0 km**
- best prototype step count: **190**
