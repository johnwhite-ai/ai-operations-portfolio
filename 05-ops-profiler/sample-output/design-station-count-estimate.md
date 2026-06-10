# Sample Engagement — Pick Station Count Estimate

*One of ~15 analytical outputs the tool generates. Shows the first-principles sizing method — every number traces to a source, every assumption is stated. Anonymized.*

**Scope:** B2C + Parts small-parts operation, 10-hour shift
**Method:** First-principles throughput model from FY line data

## Inputs

| Parameter | Value | Source |
|-----------|-------|--------|
| Design lines/day (P95) | 1,640 | order percentiles |
| Shift length | 10 hr | scope definition |
| Productive hours | 8.5 | 85% utilization assumption |
| Target lines/station/hr | 120 | goods-to-person spec |

## Calculation

```
Design lines/day (P95)        = 1,640
Productive station-hours/day  = 8.5
Lines per station per day     = 120 × 8.5 = 1,020
Stations needed (P95)         = 1,640 / 1,020 = 1.61 → 2  (steady-state)

Peak-day stress (P99 = 2,910):
  2,910 / 1,020 = 2.85 → 3 stations

With redundancy + operational buffer → 6 stations recommended
```

## Recommendation

| Scenario | Stations | Rationale |
|----------|----------|-----------|
| Steady-state (P95) | 2 | Handles 95% of days |
| Peak coverage (P99) | 3 | Handles 99% of days |
| **Recommended** | **6** | Redundancy, future growth, peak surge |

**Confidence:** Estimated — based on standard goods-to-person throughput specs. Validate against live benchmarks during pilot.

---

*The point: a hiring manager can see the math, the inputs, the sources, and the explicit assumption (85% utilization). Nothing is a black box. This is what made the output defensible in a design review.*
