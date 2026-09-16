# Recursive metric and clustering — no natural clusters (T07)

Status: research note (bounded empirical, negative result)
Scope: recursive structural metric and its clustering behaviour
Stability: one definition, one negative clustering result, no proof
Thread: T07

## Context

T07 asks whether a finer structural metric than `node_count` changes
the fingerprint classification. This note records an attempt at
defining such a metric from shape structure alone, and the clustering
result it produces.

## Setup

A recursive metric `d` on canonical shapes is defined by:

- `d(Leaf, Leaf) = 0`
- `d(Leaf, Container) = d(Container, Leaf) = 1`
- `d(a, b)` for containers =
    `abs(len(a.terms) - len(b.terms))`
  + `abs(deep_branches(a) - deep_branches(b))`
  + sum over common positions of `d(a.terms[i].exponent, b.terms[i].exponent)`

where `deep_branches(s)` is the number of non-leaf exponents at the
first level of `s`.

The metric uses no free parameter. All costs are 1.

## Result 1 — the metric is a structural rewriting of `structural_distance`

Compared on 15 pairs of integer shapes, the recursive metric and
`structural_distance_numbers` agree exactly on 11 pairs. On the
remaining 4, they differ by 1.

They are not identical, but they capture the same notion. The
recursive metric can be seen as a structural reading of
`structural_distance`, derived from width and child structure.

## Result 2 — no natural clusters

Shapes of size up to `node_count = 11` (65 shapes) were clustered
agglomeratively under the recursive metric. The merge distances grow
continuously:

    1.00, 1.00, ..., 1.25, 1.50, ..., 2.00, ..., 3.52, 4.23

No gap, no plateau, no separation.

The same experiment under `structural_distance_shapes` on shapes up to
`node_count = 9` (23 shapes) gives the same behaviour:

    1.00, 1.00, ..., 1.50, 1.67, ..., 2.90, 3.00, 3.88

No gap.

## Boundary

This note does not claim:

- that the recursive metric is new (it is not: it overlaps with
  `structural_distance`);
- that no clustering exists at all (only that none appears on small
  shapes under these two metrics);
- that the metric is canonical or optimal;
- that larger shapes would behave differently (untested).

## Interpretation

Two readings are possible:

1. Small shapes are uniformly distributed in distance space. No family
   structure exists at small sizes.
2. The metrics are too smooth: they interpolate between shapes, so
   every shape is roughly equidistant from every other.

Distinguishing between the two would require larger shapes or a
different metric.

## Reproducibility

Shape generation: Catalan recursion, cached.
Clustering: agglomerative with average linkage, no external library.
All runs complete in seconds up to `node_count = 11`.

## Status

Negative result for T07. To be extended, refuted, or archived.
