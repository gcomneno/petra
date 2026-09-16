# Reduction dominance in 3n+k maps (P2)

Status: research note (bounded empirical)
Scope: reduction/expansion profile of 3n+k maps in PETRA shape space
Stability: bounded empirical; corrects a claim in
           arithmetic-maps-structural-fingerprint.md
Thread: P2

## Context

`arithmetic-maps-structural-fingerprint.md` recorded that Collatz is
reduction-dominant and that no other tested map shares the profile.
The tested maps were `phi`, `n+1`, `n+2`, `n+3`, `2n+1`. The claim was
"Collatz is the only map in this set with a clear reduction-dominant
profile".

P2 asks whether Collatz is the only map with this property, or whether
a counterexample exists.

## Method

For each odd `k` and each starting value `n0`, the map

    n -> n/2        if n even
    n -> 3n + k     if n odd

is iterated until a cycle is reached or a bound is exhausted. The
trajectory is converted to PETRA shapes, and each consecutive
transition is classified as reduction, expansion, or stable by
`node_count`.

## Result — counterexample

The claim is refuted. Every tested `3n+k` (k odd) is reduction-dominant.

| k | n0 | steps | red% | exp% | stab% |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 27 | 112 | 56.2 | 31.2 | 12.5 |
| 1 | 97 | 119 | 56.3 | 31.1 | 12.6 |
| 1 | 871 | 179 | 56.4 | 29.1 | 14.5 |
| 3 | 27 | 20 | 55.0 | 35.0 | 10.0 |
| 3 | 97 | 27 | 55.6 | 33.3 | 11.1 |
| 3 | 871 | 118 | 55.9 | 31.4 | 12.7 |
| 5 | 27 | 34 | 52.9 | 35.3 | 11.8 |
| 5 | 97 | 11 | 54.5 | 36.4 | 9.1 |
| 5 | 871 | 57 | 54.4 | 31.6 | 14.0 |
| 7 | 97 | 43 | 53.5 | 34.9 | 11.6 |
| 7 | 871 | 51 | 56.9 | 33.3 | 9.8 |
| 9 | 97 | 15 | 53.3 | 33.3 | 13.3 |
| 9 | 871 | 57 | 54.4 | 33.3 | 12.3 |
| 11 | 27 | 31 | 54.8 | 29.0 | 16.1 |
| 11 | 97 | 27 | 51.9 | 29.6 | 18.5 |
| 11 | 871 | 55 | 54.5 | 30.9 | 14.5 |

Every row has `red > exp`, with margins between +14 and +25 points.
Collatz (k=1) is reduction-dominant, but not more than the other
`3n+k` maps by a wide margin.

## Corrected claim

The original claim was stated against a control set of linear and
multiplicative maps (`n+1`, `n+2`, `n+3`, `2n+1`, `phi`). Against that
set, Collatz was the only reduction-dominant map.

The corrected distinction is not "Collatz vs everything else". It is:

- maps with the factor 3 in the odd branch (`3n+k`, k odd) are
  reduction-dominant;
- linear maps and `phi` are balanced or expansion-dominant.

The factor 3, not the specific value k=1, is what produces the
structural reduction.

## Open question

Why does the factor 3 produce reduction dominance, and the factor 2 in
`2n+1` does not? A structural argument would need to explain what
`3n+k` does to the exponent multiset of `n` that `2n+1` does not.

## Boundary

This note does not claim:

- that all `3n+k` are reduction-dominant (tested on k in {1,3,5,7,9,11});
- that reduction dominance is a theorem about any of these maps;
- that the profile is invariant under composition or iteration;
- that the margins are stable beyond the tested bounds.

## Reproducibility

`tools/research/collatz_like_profile.py` with defaults reproduces the
table above.

## Status

First result of P2. Corrects the claim in
`arithmetic-maps-structural-fingerprint.md`.
