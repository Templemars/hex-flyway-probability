# Spring-only synthesis: Svalbard versus Netherlands

## Scope
This is a provisional synthesis using the current **spring-only** comparisons for:
- Svalbard spring
- Netherlands spring

It is intentionally limited. It summarizes what appears shared across the two spring cases, what differs between them, and what should remain provisional until autumn cases are added.

## Shared pattern across both spring cases
The main shared result is that **wind remains central** in both populations. In both Svalbard spring and Netherlands spring, the best and top-ranked RMSE solutions place substantial weight on wind support. That suggests the H3 routing framework is not producing good flyway reconstructions from arbitrary coefficient mixtures. Instead, it repeatedly selects solutions in which wind assistance is an important part of the explanation.

## Population-specific difference
The two spring populations do **not** favor exactly the same coefficient regime.

- **Svalbard spring**
  - best RMSE: **508.9 km**
  - best behavior weights: **(0.8, 0.0, 0.2, 0.0)**
  - interpretation: top solutions are more strongly **wind-dominant**

- **Netherlands spring**
  - best RMSE: **437.9 km**
  - best behavior weights: **(0.5, 0.0, 0.5, 0.0)**
  - interpretation: top solutions place relatively more emphasis on **distance alongside wind**

This suggests that the same H3 modeling framework may be flexible enough to capture population-specific movement regimes, rather than collapsing both spring cases to one generic optimum.

## Route-family structure difference
The top-20 route families also differ structurally.

- mean top-20 longitude spread, **Svalbard spring**: **8.92 degrees**
- mean top-20 longitude spread, **Netherlands spring**: **7.27 degrees**

So under the current benchmark metric, the Svalbard spring top-20 family is broader than the Netherlands spring top-20 family. That means the Svalbard benchmark currently tolerates a wider family of good H3 routes, whereas the Netherlands benchmark appears to select a somewhat tighter corridor.

The widest latitude-band spread also differs:
- Svalbard spring widest band: **(10, 20]** with spread **17.74 degrees**
- Netherlands spring widest band: **(-20, -10]** with spread **14.55 degrees**

That suggests the two populations are not only different in coefficient preference, but also different in where route-family flexibility is concentrated along latitude.

## What this means scientifically, for now
At this stage, the safest interpretation is:
- the H3 model appears able to reproduce meaningful aspects of both spring flyways
- wind importance is shared across populations
- but the details of the preferred movement regime are not identical between Svalbard and Netherlands spring

That is encouraging, because it means the framework is not trivially overfitting one single route logic. At the same time, it is still too early to generalize strongly across seasons.

## What remains provisional
This synthesis should remain explicitly provisional because:
- it uses only **spring** cases
- the endpoint rules are still prototype choices tied to the benchmark summaries
- the current validation metric is still based on 10-degree latitude-band longitude summaries
- autumn cases may reveal whether the current differences are population-specific, season-specific, or both

## Recommended next step
Extend the same workflow to the autumn simulations, then revisit this synthesis as a broader **population-by-season comparison** rather than treating the present spring-only pattern as final.
