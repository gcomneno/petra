# Shape multiplicity: many integers, few shapes (P4)

Status: research note (bounded empirical)
Scope: how many integers share a given PETRA shape
Stability: bounded empirical observation; not a theorem
Thread: P4

## Context

PETRA is shape-first. The conversion `n -> shape(n)` is not injective:
many integers share the same shape. This note measures the loss.

## Method

For each `N` in `{100, 1000, 10000}`, count the number of integers
`n <= N` for each distinct shape, keyed by mother notation.

## Result

| N | distinct shapes | shapes appearing once | most frequent shape | max count |
| ---: | ---: | ---: | --- | ---: |
| 100 | 13 | 3 | `○^(A × B)` | 30 |
| 1000 | 30 | 7 | `○^(A × B)` | 288 |
| 10000 | 64 | 13 | `○^(A × B)` | 2600 |

Distinct shape count grows sublinearly: from 13 to 64 over a
hundredfold increase in `N`. The maximum count grows roughly linearly.

## Top shapes at N = 10000

| count | shape |
| ---: | --- |
| 2600 | `○^(A × B)` |
| 1800 | `○^(A × B × C)` |
| 1229 | `○^(A)` |
| 1094 | `○^(A^(A) × B)` |
| 1011 | `○^(A^(A) × B × C)` |
| 429 | `○^(A × B × C × D)` |
| 298 | `○^(A × B^(A) × C)` |
| 230 | `○^(A^(A) × B × C × D)` |
| 219 | `○^(A^(A) × B^(A) × C)` |
| 162 | `○^(A^(A^(A)) × B)` |

The top 10 shapes cover 9272 of the 10000 integers (92.7%). The top
two shapes cover 4400 (44%).

The most frequent shape is always `○^(A × B)`: the semiprimes with
distinct primes. This is expected: they are more numerous than primes
and more numerous than any other single-exponent pattern at these
sizes.

## Interpretation

The shape is a very coarse descriptor. At `N = 10000`, most integers
collapse onto a small number of shapes, and the count per shape is
large. Two integers with the same shape can differ in every prime
involved and in every exponent that is not itself prime.

The loss is not "small noise". It is the dominant effect.

## Boundary

This note does not claim:

- an asymptotic formula for the number of distinct shapes up to `N`
  (untested);
- that the growth rate is linear or sublinear in general (only
  observed up to `N = 10000`);
- that the top shapes remain the same at larger `N`;
- that the observed concentration is stable across `N` beyond the
  three sampled values.

## Reproducibility

`tools/research/shape_multiplicity.py --ns 100 1000 10000`.

## Status

P4 closed. Negative result: shape multiplicity is large and
concentrated on a small number of shapes.
