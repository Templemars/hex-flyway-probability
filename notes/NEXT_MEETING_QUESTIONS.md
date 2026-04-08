# Questions for next brainstorming session

## Scientific framing

1. What is the strongest headline claim we want this project to make?
2. Are we modelling individual route choice, population-level occupancy, or both?
3. What is the main biological advantage of the Markov approach over least-cost paths?

## Model structure

4. What should one movement step represent?
5. Should the process be memoryless at first?
6. Do we need destination attraction in the first model version?
7. Should food be included immediately, or only after a wind-plus-distance baseline?

## Validation

8. What should be the main validation metric?
9. Do we compare against full tracks, summary flyways, or both?
10. What would count as a real improvement over the previous project?

## Project design

11. What are the minimum results needed for a publishable first paper?
12. Which parts should be prototype-only and which should be built as reusable code from the start?

## Added on 2026-04-08 for tomorrow's restart

Key open discussion points to resume from:

- choose the single tern population / flyway to start with
- define a fair square-versus-hex comparison
- decide on the metric set:
  - RMSE to decadal mean flyway as primary
  - plus at least one secondary positional metric
- decide whether crosswind enters the first coarse model set or only later
- design the first coarse weight-set table
- keep the paper structure conceptually separated into:
  - decadal mean validation
  - interannual variability
  - behavioural flexibility
  - Markov as a secondary extension
- decide whether to quantify polar distortion / grid geometry explicitly, not only predictive fit

Current scientific framing:

- Dijkstra is the main validated framework
- Markov is secondary and exploratory, used to map climatically accessible movement space
- the stronger emerging paper theme is flyway stability under interannual climatic variability and the behavioural flexibility required to maintain similar flyways
- square versus hex should be tested explicitly, ideally with the hope that hex improves fit and geometry
- start with one population first, not all tern populations at once
