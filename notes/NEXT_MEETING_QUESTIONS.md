# Questions for next brainstorming session

## Immediate technical next steps

1. How should the first H3 edge-geometry script be structured so it exposes source, target, bearing, and true edge distance transparently?
2. What is the cleanest first formulation of movement cost on the H3 grid using the agreed coefficient ordering:
   - `a = wind`
   - `b = crosswind`
   - `c = distance`
   - `d = food`
3. What should the first H3 cost-construction script output as tables, figures, and report summaries?

## Scientific design checks

4. Is the current H3 environmental assignment method sufficient for the first prototype, or do we already see a reason to upgrade beyond nearest-neighbor centroid sampling?
5. At what point should we switch from geometry/environment preparation into the first Dijkstra path calculation for Svalbard spring?
6. Which benchmark-only artifacts should remain reference-only, and which should become active comparison targets in the next phase?

## Literature / framing

7. Which additional 5 to 10 papers should enter the first literature batch next?
8. Which of those papers are core, methods, or background?

## Process reminder

This file is a rolling current agenda only.
Resolved or stale items should be removed rather than accumulated.
