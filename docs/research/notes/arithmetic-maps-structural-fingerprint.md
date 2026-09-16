# Arithmetic maps — structural fingerprint (bounded empirical)

Status: research note
Scope: reduction/expansion profile of integer maps in PETRA shape space
Stability: bounded empirical observation; not a theorem

This note records a second observation about PETRA shape space as a
setting for analyzing integer-valued dynamical systems. It extends the
Collatz structural signature note with a cross-system comparison.

## Context

A previous note (`collatz-structural-signature.md`) recorded that the
Collatz trajectory visits a small number of shapes and has a dominant
transition (semiprime to prime) that reflects the halving operation.

This note asks a broader question: does the shape-space reduction
profile differ between arithmetic maps? If yes, the profile may act as
a structural fingerprint of a map.

## Method

For each map `f` and starting value `n0`, the experiment:

1. generates the trajectory `n0, f(n0), f(f(n0)), ...` up to a bound;
2. converts each value to its canonical PETRA shape;
3. computes `node_count` of each shape (an iterative node counter);
4. classifies each consecutive transition:
   - reduction if `node_count(b) < node_count(a)`
   - expansion if `node_count(b) > node_count(a)`
   - stable if equal;
5. reports the percentage of each class over the whole trajectory.

`node_count` is defined as the number of Leaf, Container, and Term
nodes in the shape. It is independent of the numeric value of the state.

## Observation 1 — Collatz is reduction-dominant

Across five starting values in three magnitude ranges:

| Start | Steps | Reduction | Expansion | Stable |
| ---: | ---: | ---: | ---: | ---: |
| 27 | 112 | 56.8% | 30.6% | 12.6% |
| 97 | 119 | 56.8% | 30.5% | 12.7% |
| 871 | 179 | 56.7% | 28.7% | 14.6% |
| 6171 | 262 | 58.2% | 29.9% | 11.9% |
| 837799 | 525 | 59.4% | 28.1% | 12.6% |

Range: reduction 56.7 to 59.4 percent. Collatz is always
reduction-dominant by a margin of at least 26 percentage points over
expansion.

## Observation 2 — Control maps do not share the profile

Other integer maps tested:

| Map | Start | Reduction | Expansion | Stable |
| --- | ---: | ---: | ---: | ---: |
| phi (Euler totient) | 99999999 | 50.0% | 29.2% | 20.8% |
| phi | 1000000 | 50.0% | 27.8% | 22.2% |
| n+1 | 27 | 40.5% | 41.5% | 18.1% |
| n+1 | 1000 | 39.8% | 40.1% | 20.1% |
| n+2 | 27 | 35.8% | 37.1% | 27.1% |
| n+2 | 1000 | 39.1% | 38.8% | 22.1% |
| n+3 | 27 | 39.8% | 40.8% | 19.4% |
| 2n+1 | 27 | 33.3% | 41.0% | 25.6% |
| 2n+1 | 3 | 41.0% | 46.2% | 12.8% |

phi sits exactly at the reduction/expansion balance point. Linear maps
n+1, n+2, n+3 show approximately balanced profiles. The explosive map
2n+1 is expansion-dominant.

Collatz is the only map in this set with a clear reduction-dominant
profile. The set was `phi`, `n+1`, `n+2`, `n+3`, `2n+1`; later work
(`collatz-like-reduction-dominance.md`) shows that all `3n+k` (k odd)
are also reduction-dominant. The distinction is `3n+k` vs linear maps,
not Collatz vs everything else.

## Observation 3 — The profile is stable across scales

Collatz has been tested on trajectories ranging from 112 to 525 steps
and starting values from 27 to 837799. The reduction percentage stays
within a 3-point band (56.7 to 59.4).

The same stability holds for the control maps where multiple starting
values were tested.

## Observation 4 — Transition-level signature

The dominant shape-to-shape transition in Collatz trajectories is
consistently a structural reduction:

- start 27: semiprime -> prime (24x)
- start 837799: three primes -> two primes (71x)

Both are factor removals. In n+1, the dominant transition includes
self-loops (semiprime -> semiprime) and expansions (semiprime ->
p^2 times q). The structural character of the two dynamics is therefore
different at the level of single transitions, not only at the aggregate
level.

## Interpretation

The Collatz map is known for its value-level oscillation: odd steps
increase the value, even steps decrease it. The shape-space view
suggests that, structurally, the map performs a net reduction of the
recursive shape. The value grows and shrinks; the shape predominantly
shrinks.

No comparable structural statement is made here about other maps.

## Boundary

This note does not claim that:

- Collatz is solved or partially solved;
- the reduction dominance is a theorem about all Collatz trajectories;
- the profile is a rigorous invariant under composition or iteration;
- the observed 3-point band is a mathematical constant;
- node_count is the only reasonable measure of structural size;
- the classification captures every structural distinction of interest;
- similar profiles for two maps imply any deep equivalence.

The observation is bounded to the tested maps, starting values, and step
bounds.

## Reproducibility

All results were produced with:

- `resolver.int_to_shape` for value-to-shape conversion;
- `petra.parse_shape` and the public shape model for node counting;
- direct iteration of each map with a hard step bound.

No precomputed tables or external datasets were used.

## Possible next directions

1. Extend the set of tested maps:
   - aliquot sequences that enter long cycles;
   - maps involving modular reduction;
   - bit-level maps such as Collatz-like rules on binary expansions.
2. Use a finer structural measure than node_count:
   - depth-weighted mass;
   - recursive-mass metric;
   - canonical form length.
3. Test whether two different parameterizations of the same map produce
   the same profile.
4. Test whether the profile of Collatz is invariant under the map 3n-1
   (a mirror variant).
5. Investigate whether reduction dominance correlates with any known
   dynamical property.

Each direction requires a separate bounded experiment.

## Status

This note is a second bounded observation. It should be extended,
refuted, or archived based on further experiments. It is not a claim
about any deep mathematical property of Collatz.
