# Functoriality of the fingerprint: partial result (T02)

Status: research note (bounded empirical, partial)
Scope: whether transformations T on sequences admit F_T such that
       fingerprint(T(f)) = F_T(fingerprint(f))
Stability: positive for two transformations on a bounded sample;
           no proof, no general statement
Thread: T02

## Context

T02 asks: for which transformations `T` on sequences does there exist
a well-defined map `F_T` on fingerprints such that

    fingerprint(T(f)) = F_T(fingerprint(f))?

If such `F_T` exists, the fingerprint of the transformed sequence is
recoverable from the fingerprint of the original, without rebuilding
the sequence.

## Method

A bounded sample of bases `b in [2, 40]` is used, with `N = 60`. For
each base, the sequence `shape(b^n)` for `n in [1, 60]` is generated.
The fingerprint is the triple `(red%, exp%, stab%)` over consecutive
transitions.

Bases are grouped by their fingerprint. Two transformations are
tested:

- `shift`: `seq -> seq[1:]`;
- `double`: `seq -> [x, x for x in seq]`.

The test: for each fingerprint class, the transformed sequences of all
bases in that class must have the same fingerprint. If yes, an `F_T`
exists on this sample.

## Result — 6 fingerprint classes

At `N = 60` and `b in [2, 40]`, the fingerprint classes are:

| fingerprint | count | representative bases |
| --- | ---: | --- |
| (37.29, 40.68, 22.03) | 29 | 2, 3, 5, 6, 7, 10, 11, 12, ... |
| (32.2, 35.59, 32.2) | 4 | 4, 9, 25, 36 |
| (38.98, 42.37, 18.64) | 2 | 8, 27 |
| (30.51, 33.9, 35.59) | 1 | 16 |
| (40.68, 42.37, 16.95) | 2 | 24, 40 |
| (35.59, 40.68, 23.73) | 1 | 32 |

The classes appear to follow the **shape of the base** (max exponent,
factorization structure), not the value.

## Result — shift and double pass on this sample

For both `shift` and `double`, bases in the same fingerprint class
produce the same transformed fingerprint. So an `F_shift` and an
`F_double` exist on this sample.

## Boundary

This note does not claim:

- that `F_T` exists for shift or double in general;
- that the 6 classes are exhaustive or stable across `N`;
- that the classification by shape-of-base is a theorem;
- that other transformations (scaling, composition, reversal) behave
  the same way.

The test is a bounded check, not a proof. Larger samples and more
transformations are needed to say more.

## Reproducibility

Ad-hoc script in the session; not committed. The fingerprint function
is `resolver.fingerprint.fingerprint_window`.

## Status

T02 partially explored. Positive bounded result for shift and double.
General question remains open.
