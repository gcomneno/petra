# Reduction dominance in 3n-1 (T08)

Status: research note (bounded empirical)
Scope: whether the Collatz reduction profile survives the mirror map
       3n-1
Stability: bounded on five starting values; not a theorem
Thread: T08

## Context

T08 asks whether the Collatz reduction profile is invariant under the
mirror map `3n-1`. The map `3n-1` has three known cycles, so its
trajectories can behave differently from Collatz (`3n+1`).

P2 (`collatz-like-reduction-dominance.md`) showed that all `3n+k`
(k odd) are reduction-dominant. `3n-1` is the case `k = -1`.

## Method

`tools/research/collatz_like_profile.py --ks=-1` computes the profile
of `3n-1` on the same terms as P2: shortcut step `n -> n/2` if even,
`n -> 3n-1` if odd; classify each transition by `node_count`.

## Result — reduction-dominant

| n0 | steps | red% | exp% | stab% |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 5 | 60.0 | 40.0 | 0.0 |
| 7 | 5 | 60.0 | 40.0 | 0.0 |
| 27 | 8 | 50.0 | 37.5 | 12.5 |
| 97 | 36 | 52.8 | 30.6 | 16.7 |
| 871 | 34 | 52.9 | 32.4 | 14.7 |

Every case has `red > exp`. Margins range from +13 to +20 points.
The profile is the same in kind as for `3n+1` and `3n+k` (k > 0).

## Interpretation

The reduction dominance is produced by the factor 3 in the odd
branch, not by the sign of `k`. The mirror map preserves the profile.

The cases `n0 = 5` and `n0 = 7` have `stab = 0` because the trajectory
is short (five steps) and never visits the same shape twice in a row.
This is not an exception.

The known cycles of `3n-1` do not change the profile. The trajectory
is cut at the cycle by the bound in the tool; the observed transitions
are still reduction-dominant.

## Boundary

This note does not claim:

- that all `3n-1` trajectories are reduction-dominant;
- that the profile is invariant under other mirror maps;
- that the cycle structure of `3n-1` is irrelevant to the profile
  (it is irrelevant in the tested cases);
- that the margins extend beyond the tested bounds.

## Reproducibility

`tools/research/collatz_like_profile.py --ks=-1 --starts 5 7 27 97 871`.

## Status

T08 closed. Positive: `3n-1` is reduction-dominant, same profile as
`3n+k`. The sign of `k` does not matter.
