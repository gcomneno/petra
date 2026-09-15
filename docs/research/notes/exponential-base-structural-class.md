# Structural class of exponential sequences: exact identity, a lemma, and two falsifications

Status: research note (bounded empirical)
Scope: structural analysis of `k^n` via the factorization of `k`
Stability: one exact identity, one provable lemma, two falsified conjectures
Thread: T01 (`open-threads.md`)

## Context

T01 asks for a pair `(inner_sequence, structural_class(base))` extracted
from an exponential sequence `k^n`, to be used in place of the full
sequence.

This note records:

- an exact identity that decomposes `shape(k^n)` in terms of the
  factorization of `k`;
- a lemma showing that duplicating an exponent does not change the
  empirical fingerprint;
- two falsified conjectures that earlier data at small `N` had
  suggested;
- a methodological warning: the empirical fingerprint `(red, exp, stab)`
  used in previous notes is window-dependent, not a stable invariant.

It does not claim a final classification of exponential sequences.

## Exact identity

Let `k = p₁^e₁ · p₂^e₂ · … · pᵣ^eᵣ` with distinct primes `pᵢ`.
For every positive integer `n`:

    shape(k^n) = C( r0^shape(e₁·n), r1^shape(e₂·n), …, r_{r-1}^shape(eᵣ·n) )

Proof. `k^n = ∏ pᵢ^(eᵢ·n)`. PETRA roots are positional, not prime-labelled
(SPEC §1.2), so the prime values `pᵢ` do not appear in the shape. Only
the multiset of exponents `{e₁, …, eᵣ}` survives. ∎

Consequences:

- the numeric values of the primes are irrelevant to `shape(k^n)`;
- only two things matter: the number of terms `r`, and the multiset
  `{e₁, …, eᵣ}`.

This is exact, not empirical.

## The pair asked by T01

Define the universal inner sequence

    ι : n ↦ shape(n)

Then every exponential sequence is a dressing of `ι` by the base:

    n ↦ C( r0^ι(e₁·n), r1^ι(e₂·n), …, r_{r-1}^ι(eᵣ·n) )

The pair is:

- `inner_sequence = ι` (universal, independent of `k`);
- `structural_class(base) = multiset {e₁, …, eᵣ}` (deterministic, no `N`).

The base contributes the multiset; the iteration index `n` is sampled
through the shifts `eᵢ · n`.

## Lemma: duplicating an exponent is neutral

For any `a` and any number `r` of repeated terms, the multiset
`{a, a, …, a}` produces the same empirical fingerprint as the singleton
`{a}`.

Proof sketch. If all exponents equal `a`, then

    node_count(shape(k^n)) = (2r − 1) + r · node_count(shape(a·n))

which is an affine function of `node_count(shape(a·n))` with positive
slope `r`. An affine transformation with positive slope preserves the
sign of every consecutive difference, hence preserves every transition
(reduction, expansion, stable). ∎

Empirically confirmed for `a = 1..10`, and for `r = 1` versus `r = 2`
across all tested values.

## Falsification 1: "the presence of 1 forces a class"

At `N = 60`, the multisets `{1}`, `{1,1}`, `{1,1,1}`, `{2,1}` all
produced the same fingerprint `(37.3, 40.7, 22.0)`. A first conjecture
was: any multiset containing a `1` collapses to that class.

Extended data falsifies this.

At `N = 500`:

| multiset | fingerprint |
| --- | --- |
| `{1}` | (40.48, 41.48, 18.04) |
| `{2,1}` | (41.08, 42.69, 16.23) |
| `{3,1}` | (41.68, 42.89, 15.43) |
| `{4,1}` | (46.29, 46.89, 6.81) |

The same class at `N = 60` dissolves by `N = 500`. The "1 wins"
conjecture is falsified.

## Falsification 2: "the fingerprint is a stable class invariant"

The fingerprint

    F(N) = (red(N), exp(N), stab(N))

is a window average of consecutive transition types. If `F` is a class
invariant, it should converge as `N → ∞`.

Disjoint-window test on `{1}`, window size 200:

| window | red | exp | stab |
| --- | --- | --- | --- |
| [1, 200] | 38.2 | 40.7 | 21.1 |
| [401, 600] | 41.7 | 43.7 | 14.6 |
| [801, 1000] | 42.7 | 40.2 | 17.1 |
| [1001, 1200] | 38.7 | 39.7 | 21.6 |
| [1801, 2000] | 41.7 | 41.7 | 16.6 |

The same multiset oscillates by roughly 7 percentage points in `stab`
across disjoint windows. The fingerprint at fixed window size is
therefore not an invariant. It is a window-dependent measurement.

Cumulative values `F(1, N)` do appear to drift slowly toward a common
region across the singletons `{1}, {3}, {5}, {11}`, while `{2}`, `{2,1}`,
and `{3,1}` remain clearly distinct. But convergence is not proven, and
its rate is not bounded. Whether a limit exists is an open question.

## Methodological warning

The fingerprint `(red, exp, stab)` introduced in
`sequence-structural-fingerprint-classifier.md` is a bounded empirical
measure. It is not stable under window choice, and it does not by itself
define a class. Any use of it as a classifier must declare the window
size and, ideally, the cumulative behaviour.

Structural identities (such as the exact identity above) are unaffected
by this warning. They hold at every `n`, not on average.

## Open questions

1. Does the cumulative fingerprint `F(1, N)` converge as `N → ∞`?
   No tool in this project currently decides this.
2. If it does, what is the limit for each multiset, and does the limit
   separate classes cleanly?
3. Is the window-independence recoverable by a different statistic
   (transition matrix, Markov chain on shape-to-shape pairs)?
4. Does the decomposition recurse into the exponents themselves?
   The term `shape(e·n)` is itself a container of exponent shapes, and
   the same `ι` reappears at every depth. This is a natural next
   direction and is not addressed here.

## Boundary

This note does not claim:

- a final classification of `k^n` by structural class;
- that any two tested multisets are truly in the same class;
- that `node_count` is the correct metric;
- that convergence of the cumulative fingerprint holds or fails;
- that the "class" is well-defined in the absence of a proven invariant.

## Reproducibility

All results use:

- `sympy.factorint` on the base only;
- `shape(k^n)` built directly by multiplying each exponent `eᵢ` by `n`;
- `resolver.int_to_shape` for recursive construction;
- `node_count` on canonical shapes;
- transition classification over `n = 1..N`.

Scripts are not committed as part of this note; the methods are simple
enough to be re-run from the description above.

## Status

First structural result of T01. The exact identity and the duplication
lemma are solid. The classification is not. This note replaces the
earlier conjecture-level reading of the fingerprint collisions at
`N = 60` and should be read together with
`sequence-structural-fingerprint-classifier.md`.
