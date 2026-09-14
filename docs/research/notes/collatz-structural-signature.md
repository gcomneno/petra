# Collatz structural signature (bounded empirical)

Status: research note
Scope: structural trajectory of the Collatz map in PETRA shape space
Stability: bounded empirical observation; not a theorem

This note records an empirical observation about the Collatz trajectory
in PETRA canonical shape space. It does not claim to resolve Collatz,
nor to establish a general theorem. It records a reproducible pattern.

## Background

The Collatz map is defined on positive integers:

    n -> n / 2       if n is even
    n -> 3 * n + 1   if n is odd

It is conjectured that every trajectory reaches the cycle 4 -> 2 -> 1.

This note does not address the conjecture. It studies the sequence of
canonical PETRA shapes visited by a Collatz trajectory, using the
Resolver's `int_to_shape` conversion and the canonical textual
serialization as the shape label.

## Method

For each starting integer `n0`:

1. generate the Collatz trajectory `n0, n1, n2, ...` up to the value 1;
2. convert each value to its canonical PETRA shape;
3. label each shape by its canonical text;
4. count distinct shapes, shape frequencies, and shape-to-shape
   transitions.

The result is a trajectory in **shape space**, not in value space. The
shape space is a small finite alphabet for bounded ranges, so the
trajectory can be analyzed as a sequence over an alphabet.

## Observation 1 — Shape space is a small alphabet

For the trajectory starting at 27 (112 values):

- distinct shapes: **13**
- top-4 shapes cover 93 of 112 states (83%)
- top shape: `C(r0^1,r1^1)` (semiprime), 36x
- second shape: `C(r0^1)` (prime), 25x

The value sequence 27, 82, 41, 124, 62, ... has no visible structure.
Its shape sequence is a walk over 13 labels.

## Observation 2 — The transition grammar is stable across scales

The top-5 shape transitions are the same for trajectories of very
different lengths:

| Starting value | Steps | Dominant transitions |
| ---: | ---: | --- |
| 7 | 17 | S->P, P->S, P->Q, Q->S, Q->Q |
| 27 | 112 | S->P, T->S, Q->S, P->T, P->S |
| 97 | 119 | S->P, T->S, Q->S, P->T, S->S |
| 871 | 179 | S->P, T->S, Q->S, U->T, S->S |
| 6171 | 262 | S->P, T->S, Q->S, U->T, Q->Q |
| 77031 | 351 | T->S, S->P, T4->T, U->T, Q->S |
| 837799 | 525 | T->S, S->P, T4->T, Q->S, U->T |

Legend:

- P = `C(r0^1)` (prime)
- S = `C(r0^1,r1^1)` (semiprime)
- Q = `C(r0^C(r0^1),r1^1)` (`p^2 * q`)
- T = `C(r0^1,r1^1,r2^1)` (three distinct primes)
- T4 = `C(r0^1,r1^1,r2^1,r3^1)` (four distinct primes)
- U = `C(r0^C(r0^1),r1^1,r2^1)` (`p^2 * q * r`)

The transition `S -> P` (semiprime to prime) dominates across all
tested trajectories. It is the structural signature of the halving
operation `2p -> p`.

## Observation 3 — The signature is not generic

A control experiment replaced each Collatz value with a random integer
within +/-20% of that value, keeping the trajectory size profile
identical. The shape transition distribution changed substantially:

| Rank | Collatz(27) | Random at same scale |
| ---: | --- | --- |
| 1 | S->P (24x) | S->S (13x) |
| 2 | T->S (12x) | T->T (6x) |
| 3 | Q->S (11x) | P->S (5x) |
| 4 | P->T (8x) | T->S (4x) |
| 5 | P->S (6x) | S->U (4x) |

Only 2 of 5 top transitions are shared. The two shared ones are the
weakest. Collatz trajectories are dominated by structural **reduction**
(S->P, T->S, Q->S), while random trajectories of the same scale show
self-loops (S->S, T->T) and structural growth (S->U).

## Observation 4 — Changing the rule changes the signature

The variant `5n+1` from the same starting value 27 collapses to a
trivial trajectory in 11 steps. The variant `7n+1` did not converge
within a 5000-step guardrail during the experiment.

The `3n+1` signature (dominant S->P) is therefore not a property of
"any odd-multiplier Collatz-like rule". It depends on the specific
arithmetic of the 3n+1 map.

## Boundary

This note does not claim that:

- Collatz is resolved or partially resolved;
- the observed transition grammar is a theorem about all trajectories;
- the shape space analysis extends to unbounded integers without
  resource limits;
- the "signature" is unique to Collatz beyond the tested variants;
- the pattern has any consequence for the Collatz conjecture itself.

The observation is bounded to the tested starting values and to the
tested Collatz-like rules.

## Reproducibility

All results were produced with:

- `resolver.int_to_shape` for value-to-shape conversion;
- `petra.serialize_shape` for canonical shape labels;
- a direct Collatz iteration with a hard step limit of 5000.

No precomputed tables or external datasets were used.

## Possible next directions

1. Study other recursive integer dynamics:
   - `n -> phi(n)` (Euler totient);
   - `n -> sigma(n) - n` (aliquot sequence);
   - `n -> n / rad(n)` (radical removal);
   - `n -> n + 1` (baseline).
2. Compare the structural signature of each map with Collatz.
3. Test whether other trajectories (not just starting values) produce
   different dominant transitions.
4. Extend the alphabet to larger integer ranges and observe whether
   new structural motifs emerge.

Each direction requires a separate bounded experiment.

## Status

This note is a first bounded observation. It should be extended,
refuted, or archived based on further experiments.
