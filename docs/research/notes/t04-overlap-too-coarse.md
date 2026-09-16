# Meet/join overlap is too coarse for clustering (T04)

Status: research note (bounded empirical, negative)
Scope: whether `structural_overlap = node_count(meet) /
       node_count(join)` can be used to cluster shapes
Stability: bounded measurement on `N = 500`
Thread: T04

## Context

T04 proposed using meet and join to cluster numbers by structural
similarity. `overlap(a, b) = node_count(meet) / node_count(join)` is
already implemented in `resolver.structural_algebra`.

This note measures whether the overlap can discriminate.

## Method

For every pair `(n, m)` with `2 <= n < m <= 500`, compute
`overlap(shape(n), shape(m))`, rounded to two decimals. Count the
distribution.

Total pairs: 124251.

## Result

Only 17 distinct overlap values occur. The distribution is
concentrated on a few of them:

| overlap | count | share |
| ---: | ---: | ---: |
| 0.71 | 22950 | 18.5% |
| 1.00 | 20440 | 16.4% |
| 0.56 | 18614 | 15.0% |
| 0.43 | 16805 | 13.5% |
| 0.60 | 15200 | 12.2% |
| 0.33 | 8956 | 7.2% |
| 0.78 | 7684 | 6.2% |
| 0.45 | 6173 | 5.0% |
| other 9 | 7429 | 6.0% |

The top 6 values cover 83% of all pairs.

The values are ratios of odd integers (`node_count` is always odd for
a canonical shape): 5/7, 5/9, 3/7, 3/5, 1/3, 7/9, 5/11, 7/11, ...

The value 1.00 has 20440 pairs: this is the number of pairs with the
same shape. Since `N = 500` and there are only a few dozen shapes,
this is expected.

## Interpretation

The overlap is a very coarse descriptor. It collapses 124251 pairs
into 17 buckets, and the first 6 buckets contain 83% of the pairs.
It cannot serve as a clustering metric by itself.

The reason is structural: the overlap is a single rational number,
and `node_count` takes only small odd values on small shapes. The
number of distinct ratios is bounded by the number of distinct
`(node_count(meet), node_count(join))` pairs, which is small.

## Boundary

This note does not claim:

- that the overlap is useless in general (it may work as one feature
  among many);
- that meet and join cannot be used for clustering (only that the
  scalar overlap is too coarse);
- that the concentration is stable for larger `N` (untested).

## Reproducibility

Ad-hoc script in the session; not committed.

## Status

T04 closed. Negative: the overlap is too coarse to cluster shapes.
