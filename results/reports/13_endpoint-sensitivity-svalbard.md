# Endpoint sensitivity for Svalbard spring

## Question
How sensitive are the four current extreme-behavior routes to small changes in start and end H3 cells around the reference validation endpoints?

## Setup
- reference start cell: `83eea8fffffffff`
- reference end cell: `83076bfffffffff`
- tested behaviors: `support_only`, `crosswind_only`, `distance_only`, `food_only`
- tested start cells: reference cell plus randomly sampled cells from its H3 k=2 neighborhood
- tested end cells: reference cell plus randomly sampled cells from its H3 k=2 neighborhood
- random seed: `42`
- output route table kept intentionally compact, with coordinates only

## Outputs
- route coordinates: `results/tables/13_svalbard_endpoint_sensitivity_coordinates.csv`
- tested endpoint pairs: `results/tables/13_svalbard_endpoint_sensitivity_endpoints.csv`
- overlay figure: `results/figures/13_svalbard_endpoint_sensitivity_routes.png`

## Quick-look maps

### Support map
![Endpoint sensitivity over four background cost maps, support panel](../figures/13_svalbard_endpoint_sensitivity_routes.png)

### Crosswind map
![Endpoint sensitivity over four background cost maps, crosswind panel](../figures/13_svalbard_endpoint_sensitivity_routes.png)

### Distance map
![Endpoint sensitivity over four background cost maps, distance panel](../figures/13_svalbard_endpoint_sensitivity_routes.png)

### Food map
![Endpoint sensitivity over four background cost maps, food panel](../figures/13_svalbard_endpoint_sensitivity_routes.png)

## Map styling
- reference least-cost path shown in **red**
- alternative endpoint-sensitivity routes shown in **grey**
- backgrounds use the usual four component cost maps for direct comparison

## Run summary
- successful routes across all tested behavior-endpoint combinations: **324**
