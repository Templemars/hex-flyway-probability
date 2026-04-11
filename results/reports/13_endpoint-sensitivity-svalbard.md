# Endpoint sensitivity for Svalbard spring

## Question
How sensitive is the current Svalbard spring prototype to small changes in start and end H3 cells around the reference validation endpoints?

## Setup
- reference behavior: `food_only`
- reference start cell: `83eea8fffffffff`
- reference end cell: `83076bfffffffff`
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
