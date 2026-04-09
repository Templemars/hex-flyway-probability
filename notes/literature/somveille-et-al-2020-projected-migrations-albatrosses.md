# Somveille et al. 2020, projected migrations of southern Indian Ocean albatrosses

## Citation

Somveille, M., Dias, M.P., Weimerskirch, H., & Davies, T.E. (2020). *Projected migrations of southern Indian Ocean albatrosses as a response to climate change*. Ecography, 43, 1683–1691.

## Why this paper matters for the project

This paper is very relevant methodologically because it applies a mechanistic migratory movement model under present and future environmental conditions, using wind and chlorophyll as core drivers. That is closely aligned with our current modelling logic.

## Why it belongs in `refs/methods/`

This paper belongs in methods because it directly addresses:
- mechanistic movement simulation
- wind effects on movement
- chlorophyll as an attraction / food proxy
- calibration of model parameters against empirical tracking data
- future projection of movement patterns

These are all strongly relevant to our project.

## Main relevance from first read

The paper simulates non-breeding movements of albatrosses by:
- constructing an environmental potential landscape
- combining chlorophyll attraction with wind effects
- varying free parameters controlling the importance of wind relative to attraction to resources and the level of stochasticity
- calibrating the model against empirical tracking data

This is especially relevant because it offers a direct example of how a mechanistic bird-movement model can be:
- parameterized
- compared to tracks
- and then projected under changed climate scenarios

## What seems particularly important for us

This paper may help us with:
- thinking about parameter calibration strategy
- comparing simulated trajectories to observed movement distributions
- deciding how transparent and interpretable the model should remain when multiple environmental drivers are combined
- understanding how to frame projection work if we later extend beyond the present-day hex-grid comparison

## Relationship to our project

This is one of the strongest methods references so far because it sits very close to our own problem:
- seabird movement
- wind + chlorophyll drivers
- mechanistic route generation
- model calibration against real movement data

The main difference is that our project currently aims to build a graph-based H3 cost model with Dijkstra and later perhaps Markov extensions, whereas this paper appears to use a different movement-simulation framework.

## Follow-up

This note should later be expanded with:
- the exact movement equations and parameter meanings
- how their wind/resource potential landscape compares to our edge-cost formulation
- whether their calibration and reporting strategy should influence our own implementation plan
- whether this should be elevated to one of the most central methods references in the project
