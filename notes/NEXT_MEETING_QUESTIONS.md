# Questions for next brainstorming session

## Immediate technical next steps

1. How should RMSE be implemented for the full 216-behavior Svalbard sweep against `gdf_SS_10.csv`?
2. After RMSE ranking on Svalbard spring, should the next step be Netherlands spring or deeper inspection of the best Svalbard routes?
3. Do we need to reconstruct the paper's exact 195-filtered behavior set after the current 216-behavior bounded sweep?

## Scientific design checks

4. Is the current H3 environmental assignment method still sufficient for the first routing prototype, or do the new component maps suggest any need for refinement?
5. Has directional distance anisotropy in the H3 graph started to bias Dijkstra route geometry when distance weights are high, or does it remain a minor effect?
6. How should we interpret the diagnostic northward component maps versus the true edge-based routing quantities when presenting the method?
7. After the new efficiency rule, which upcoming steps should be split cleanly into simulation, reporting, and evaluation scripts to avoid unnecessary reruns?

## Distance red flag

Keep this explicitly alive:
- the distance term is usable, but not fully “closed” scientifically
- diagnostic northward distance maps show stronger corridor patterns than the underlying edge summary alone would suggest
- revisit distance handling if later routes look grid-directional or overly sensitive to the distance coefficient

## Algorithm red flag

Keep this explicitly alive too:
- the first Dijkstra prototype may use a package implementation for reliability and speed
- later we may still want a manual Dijkstra implementation for maximal auditability or method-validation purposes
- revisit this if package behavior becomes limiting or if we want explicit algorithm-comparison documentation

## Literature / framing

8. Which literature notes should be revisited next only if they directly affect the first Dijkstra formulation or interpretation?

## Process reminder

This file is a rolling current agenda only.
Resolved or stale items should be removed rather than accumulated.

## Literature / framing

7. Which literature notes should be revisited next only if they directly affect the first Dijkstra formulation or interpretation?

## Process reminder

This file is a rolling current agenda only.
Resolved or stale items should be removed rather than accumulated.
