# Skyllas et al. 2025, seabird flyways

## Citation

Skyllas, N. et al. (2025). *Simulating and Analysing Seabird Flyways: An Approach Combining Least-Cost Path Modelling and Machine Learning*. Global Ecology and Biogeography.

## Why this paper matters here

This is the direct scientific predecessor of the current project. It defines the previous square-grid least-cost framework, the relevant environmental trade-offs, the tern flyway validation context, and the broad scientific motivation for the sequel project.

## Role in the new project

This paper serves as:
- the methodological baseline
- the biological benchmark for tern flyways
- the source of the decadal mean flyway framing
- the comparison point for the square-versus-hex redesign

## Immediate relevance

The new project should clearly state what it inherits from this paper and what it changes:
- square grid to hex grid
- stronger focus on climate-driven flyway stability and interannual variability
- exploratory Markov extension for climatically accessible movement space

## Specific method detail to retain

For flyway evaluation in the 2025 paper:
- the median starting location of each population was used as the simulation starting point
- the median longitudinal position of each population was calculated per 10° of latitude
- each simulated flyway was also summarized as median longitude per 10° latitude band
- RMSE was then calculated by comparing the simulated and observed longitude summaries across latitude bands
- the top 20 simulations with the lowest RMSE were selected for further analysis

This is important for the new project because it means any proposed secondary validation metric should not simply duplicate the same latitude-binned longitude comparison already embedded in the RMSE method.

## Weighting strategy used in the 2025 paper

The paper used a four-component linear cost formula:
- `a` = standardised parallel wind cost
- `b` = standardised crosswind cost
- `c` = standardised distance cost
- `d` = standardised food cost

Key details:
- the four weights sum to 1
- weights were varied in increments of 0.1
- `a` and `c` were allowed to vary between 0 and 1
- `b` and `d` were allowed to vary between 0 and 0.5
- these rules yielded 195 unique component combinations

Important interpretation detail:
- high values of crosswind and food weights were limited after sensitivity analysis because larger values often produced very long and unrealistic flyways while improving RMSE only marginally

This matters for the new project because it suggests a practical precedent for starting with a constrained, interpretable coarse weight-set table rather than an unrestricted search.

## Cost-construction logic to retain for the sequel

The 2025 paper's movement model is built from **directional edge costs** rather than a simple static cell-level resistance surface.

The key logic is:
- each move is defined from a **source cell `i`** to a **target cell `j`**
- the relevant environmental and geometric quantities are computed for that directional move
- the final movement cost is then a **linear weighted combination** of four standardized components

Component structure in the paper's final notation:
- `w_cost` = standardised parallel wind cost
- `c_cost` = standardised crosswind cost
- `d_cost` = standardised distance cost
- `f_cost` = standardised food cost

Final cost formula used in the paper:
- `cost(i,j) = a * w_cost(i,j) + b * c_cost(i,j) + c * d_cost(i,j) + d * f_cost(i,j)`

Important implications:
- the model is **direction-sensitive**, because wind support and crosswind depend on the direction of movement from `i` to `j`
- this means the sequel should be built as an **edge-based graph model**, not only as a cell-based raster-like resistance layer
- the paper explicitly avoided assuming non-linear relationships between components in the final combined cost formula; the final combination is linear for interpretability

Component-specific logic retained from the methods section:
- **parallel wind cost** is based on the projection of the wind vector onto the direction of movement
- **crosswind cost** is based on the component of the wind vector perpendicular to movement direction
- **distance cost** is based on the distance from the target cell to the destination, standardized within the domain
- **food cost** is based on chlorophyll-a, treated as a food proxy and transformed into a standardized cost contribution

Important implementation caution for the sequel:
- because the sequel uses H3 and Python rather than the original square-grid / R workflow, the paper's conceptual logic should be preserved even if the exact numerical implementation details need adaptation
- before coding the full H3 cost graph, the local edge-level environmental quantities should be computed and inspected explicitly

## Follow-up

This note is currently a seed note. It should later be expanded with:
- exact methods reused
- exact limitations of the previous framework
- candidate text for manuscript framing
