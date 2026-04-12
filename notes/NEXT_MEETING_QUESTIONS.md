# Questions for next brainstorming session

## Immediate technical next steps

1. Why do the autumn full bounded runs still terminate before completion even after the sweep-core refactor, and what is the exact remaining failure mode now that the runs progress farther than before?
2. Should the next debugging step capture explicit post-run exit status and system-level kill evidence for the refactored autumn sweep, rather than attempting more blind reruns?
3. Once the sweep becomes stable enough to finish, should `svalbard_autumn_afaf` remain the first autumn validation case before retrying `netherlands_autumn`?

## Scientific design checks

4. Is the Netherlands autumn northern endpoint substitution still scientifically acceptable as a prototype benchmark-alignment rule, or does it indicate that the current ERA5-supported routing domain is too restrictive near the departure area?
5. Has directional distance anisotropy in the H3 graph started to bias Dijkstra route geometry when distance weights are high, or does it remain a minor effect?
6. How should we interpret the diagnostic northward component maps versus the true edge-based routing quantities when presenting the method, especially once autumn southward cases are added?
7. Which upcoming steps should remain split cleanly into simulation, reporting, and evaluation scripts to avoid unnecessary reruns?

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

## Process reminder

This file is a rolling current agenda only.
Resolved or stale items should be removed rather than accumulated.
