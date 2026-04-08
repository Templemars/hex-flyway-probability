# Questions for next brainstorming session

## Priority restart points

1. Which tern population / flyway should be used first?
2. What is the fairest way to compare square and hex grids?
3. Which genuinely non-redundant secondary metric should accompany RMSE, given that the 2025 paper's RMSE already used median longitude per 10° latitude band?
4. Should crosswind be included in the first coarse weight-set table or added later?
5. Should grid geometry and polar distortion be quantified explicitly, in addition to predictive fit?

## Scientific framing checks

6. Is the project scope still appropriate for one paper?
7. How should behavioural flexibility be phrased so we do not overinterpret model weights as directly observed behaviour?
8. How should the Markov section be framed so it remains clearly exploratory and biogeographical rather than competing with the main Dijkstra analysis?

## Markov-specific questions

9. Should the Markov process allow staying in place?
10. How broad should the Southern Ocean starting mask be in the first analysis?
11. Which Markov outputs should be prioritized for the paper:
   - occupancy after N steps
   - cumulative visitation probability
   - contour envelopes
   - overlap with observed flyways

## Practical next design choices

12. What should the first coarse weight-set table look like?
13. What fairness criterion should be hard-coded into the square-versus-hex benchmark design?
14. What is the minimum clean prototype needed before scaling to all years?
15. Which additional 5 to 10 papers should enter the first literature batch, and how should they be categorized into core, methods, and background?
