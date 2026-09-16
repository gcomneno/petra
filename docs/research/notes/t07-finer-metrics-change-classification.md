# Finer metrics change the fingerprint classification (T07)

Status: research note (bounded empirical, positive)
Scope: whether replacing node_count in the fingerprint with a finer
       metric changes the classification of bases
Stability: bounded on a small sample; not a theorem
Thread: T07

## Context

T07 asks whether replacing `node_count` with a finer measure changes
the fingerprint classification. `recursive-metric-no-clusters.md`
addressed a different question (a distance, not a fingerprint). This
note addresses the original one.

## Method

The `transition` function classifies `shape(base^n) -> shape(base^(n+1))`
by comparing a scalar metric `mu` on the two shapes. Four metrics are
tried:

- `node_count` (baseline);
- `depth` = maximum depth;
- `depth_mass` = sum of depths of all nodes;
- `deep_branches` = number of non-leaf exponents at the first level.

For `N = 60` and bases `b in {2, 3, 5, 6, 7, 10, 12, 15, 30}`, the
fingerprint `(red%, exp%, stab%)` is computed with each `mu`.

## Result — the classification changes

With `node_count`, all nine bases share the same fingerprint at
`N = 60`:

    (37.29, 40.68, 22.03)

With `depth`, base 12 separates:

| base | fingerprint |
| --- | --- |
| 2, 3, 5, 6, 7, 10, 15, 30 | (28.81, 30.51, 40.68) |
| **12** | (45.76, 42.37, 11.86) |

With `depth_mass`, base 12 separates more sharply, with `stab = 0`:

| base | fingerprint |
| --- | --- |
| 2, 3, 5, 6, 7, 10, 15, 30 | (42.37, 42.37, 15.25) |
| **12** | (50.85, 49.15, 0.0) |

With `deep_branches`, all bases collapse to a single class:

    (0.0, 1.69, 98.31)

The metric is too coarse: almost every transition is stable.

## Interpretation

`12 = 2^2 * 3`, so `shape(12^n) = C(shape(2n), shape(n))`: two
distinct exponents, 2 and 1. The other tested bases have the multiset
`{1, 1, ..., 1}` (or `{1}` after the duplication lemma). Only 12 has
two distinct exponents.

`depth` and `depth_mass` capture this difference. `node_count` does
not, at this `N`. `deep_branches` is blind to it.

The choice of metric is not a technical detail: it changes which
bases are separated.

## Boundary

This note does not claim:

- that `depth` or `depth_mass` are the best metrics (only that they
  change the classification);
- that `12` remains the only separated base at other `N`;
- that the classification is stable across `N` (T16/T19 shows it is
  window-dependent for `node_count`);
- that the result extends to all bases (tested on nine).

## Reproducibility

Ad-hoc script in the session; not committed. The metrics are simple
recursive functions on shapes.

## Status

T07 closed. Positive: finer metrics do change the classification.
