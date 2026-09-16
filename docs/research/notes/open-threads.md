# Open research threads

Status: living document
Scope: index of active and dormant research directions
Update rule: append new threads, update status, never delete

This document tracks every research direction that has been opened
during the PETRA research sessions. Each thread has a short description,
a minimal example, and a status.

Statuses:

- **open**: not started, no blocking dependency
- **in progress**: active work
- **blocked**: waiting for another thread or external input
- **closed**: completed; result recorded elsewhere
- **abandoned**: tried and dropped; reason recorded

## Threads

### T01 — Canonicalizer for exponential sequences

**Statement.** Extract `(inner_sequence, structural_class(base))` from a
sequence `k^n` and operate on the pair instead of the full sequence.

**Minimal example.** `12^n` and `20^n` share the same shape
`C(r0^C(r0^1), r1^1)`. The canonicalizer should produce the same
representative for both.

**Status.** in progress.

**Notes.** First result recorded in
`exponential-base-structural-class.md`: exact identity
`shape(k^n) = C(r0^shape(e₁n), …)`, a duplication lemma
(`{a,a} ≡ {a}`), and two falsified conjectures ("1 wins",
"fingerprint is a class invariant"). Classification is not settled:
the cumulative fingerprint may or may not converge.

Third result recorded in `recursive-reconstruction-t01.md`: any
canonical shape can be built from the mother in a single chain of
struct applications using only two elementary pieces, in height-first
order.

**Forward.** Continued in T16 (convergence of the cumulative fingerprint).

**Prerequisite for.** T02 (functor).

### T02 — Functoriality of the fingerprint

**Statement.** For which transformations `T` on sequences does there
exist a well-defined map `F_T` such that
`fingerprint(T(f)) = F_T(fingerprint(f))`?

**Minimal example.** `T(f) = k^f` for prime `k` seems to work.
Unclear for shift, scaling, composition.

**Status.** open.

**Depends on.** T01.

### T03 — Multiset-of-exponents invariant

**Statement.** `fingerprint(k^n)` depends only on the multiset of
exponents in the prime factorization of `k`, not on the number of
distinct primes.

**Minimal example.** `2^n`, `6^n`, `30^n` all have the same fingerprint
because their factorization exponent multisets are `{1}`, `{1,1}`,
`{1,1,1}` — all composed of 1's.

**Status.** open. Partially confirmed at N=40.

### T04 — Meet/join as clustering tools

**Statement.** Use meet and join to cluster numbers by structural
similarity. `overlap(a, b) = node_count(meet)/node_count(join)` is
already implemented.

**Minimal example.** Cluster the range `[2, 1000]` by pairwise overlap.
Compare with clustering by shape identity.

**Status.** open. `structural_algebra.py` implemented; applications not
yet explored.

### T05 — Arithmetic layer above the Resolver

**Statement.** Build a class that keeps `(shape, key)` together and
supports arithmetic operations (division, multiplication, addition) on
this pair, delegating structural edits to the canonical operators.

**Minimal example.** `12 / 3 = 4` via SHED on the shape, with the key
tracking which prime was removed.

**Status.** open.

### T06 — Structural elision as p/p = 1

**Statement.** Given `shape(p) and shape(p)` in a common context,
structural elision returns Leaf. Ambiguity arises when terms are
indistinguishable without a key.

**Minimal example.** `C(r0^1, r1^1)` could be `2*3` or `3*2`; eliding
one leaf is ambiguous without the key.

**Status.** open. Related to T05.

### T07 — Finer structural metrics

**Statement.** Replace `node_count` with a finer measure (depth-weighted
mass, recursive mass, canonical form length) and test whether the
fingerprint classification changes.

**Minimal example.** Two shapes with the same node_count but different
depths might produce different fingerprints under a depth-weighted
metric.

**Status.** open.

### T08 — Collatz on `3n - 1`

**Statement.** Test whether the Collatz reduction profile is invariant
under the mirror map `3n - 1`. The `3n - 1` map has three known cycles,
so the results may differ substantially.

**Minimal example.** Start at 5 under `3n - 1`.

**Status.** open.

### T09 — Shape-plus-context for deterministic succession

**Statement.** A pure shape does not determine the Collatz successor.
A shape together with `n mod 2^k` (for sufficient k) does. Explore
whether this "shape-plus-context" state recovers a ranking function.

**Minimal example.** `6` and `15` share a shape; `6 mod 4 = 2`,
`15 mod 4 = 3`. The two residues have different Collatz successors.

**Status.** open.

### T10 — Fingerprint catalogue

**Statement.** Build a catalogue of fingerprints for many known
sequence families. Use it to assign novel sequences to families.

**Minimal example.** Given an unlabeled sequence, compute the
fingerprint and look up the nearest catalogue entry.

**Status.** open. Related to T02.

### T11 — Beatty sequences and other non-obvious families

**Statement.** Test the fingerprint classifier on families not
generated by recurrences or algebraic formulas: Beatty sequences,
sums of two squares in enumeration order, random walks with drift.

**Minimal example.** The Beatty sequence for `sqrt(2)`.

**Status.** open.

### T12 — Invariance under sparse sampling

**Statement.** Test whether the fingerprint of a sequence changes when
sampled sparsely (every second term, every k-th term).

**Minimal example.** Fibonacci vs every-second-Fibonacci (which is
Fibonacci itself, shifted).

**Status.** open.

### T13 — Distribution of overlap in a range

**Statement.** Compute the distribution of `overlap(a, b)` across all
pairs in `[2, 1000]`. Compare with the distance distribution from the
existing distance atlas.

**Minimal example.** The distance atlas says mean distance is ~3.6.
What is the mean overlap?

**Status.** open.

### T14 — Fingerprint of Collatz trajectory itself

**Statement.** Treat the Collatz trajectory from a given start as a
sequence of values (not as a dynamical system). Compute its fingerprint.
Compare across starting values.

**Minimal example.** Compare the fingerprint of the Collatz trajectory
from 27 with that from 97.

**Status.** open.

### T15 — Structural signature of prime gaps

**Statement.** Take the sequence of prime gaps `p_{n+1} - p_n`.
Compute its structural fingerprint. Does it have a distinctive profile?

**Minimal example.** First gaps: 1, 2, 2, 4, 2, 4, 2, 4, 6, 2, 6, ...

**Status.** open.

### T16 — Convergence of the cumulative fingerprint

**Statement.** The cumulative fingerprint `F(1, N) = (red, exp, stab)`
of `k^n` is observed to drift slowly as `N` grows, but its limit is
not known to exist. Decide empirically and, if possible, analytically,
whether `F(1, N)` converges for each base `k`, and at what rate.

**Minimal example.** For `k = 2`:

- `F(1, 60)   ≈ (37.3, 40.7, 22.0)`
- `F(1, 500)  ≈ (40.5, 41.5, 18.0)`
- `F(1, 2000) ≈ (41.0, 41.1, 17.9)`

The value moves by ~3 points between `N = 60` and `N = 500`, then by
less than 0.5 points between `N = 500` and `N = 2000`. Slow
convergence, slow drift, or neither — undecided.

**Status.** in progress.

**Depends on.** T01 (decomposition and fingerprint layer).

**Prerequisite for.** A stable notion of "structural class" that does
not depend on a chosen window.

**Second result** (`t16-fingerprint-asymptotics.md`): the transition
signal of `k^n` reduces exactly to the arithmetic function
`g(n) = node_count(shape(n))`, which satisfies
`g(1) = 1`, `g(n) = 1 + sum over e in Exp(n) of (1 + g(e))`.
For `k = 2`, `transition(shape(2^n), shape(2^(n+1))) = sign(g(n+1) - g(n))`,
verified 79/79 on `n = 2..80`; the recurrence is verified 200/200 on
`n = 1..200`. The cumulative fingerprint of `g` at `N = 10^8` is
`(42.40, 42.40, 15.20)` with `red - exp -> 0` and `stab(N)` decreasing
monotonically. The asymptotic form of `stab(N)` is undecided between
`a + b/log N` with `a ~ 13` and `c/(log N)^alpha` with `alpha ~ 0.15`;
the local slope of `stab * log N` decreases monotonically from 13.50 to
13.09 over the last four decades and has not stabilised. See T19.

**Notes.** The fingerprint layer is implemented in
`resolver/src/resolver/fingerprint.py`. The motivation and the
falsification of the naive "class = window fingerprint" reading are
in `exponential-base-structural-class.md`.

### T17 — Flakiness of test_resolver under full suite

**Statement.** A test in the resolver suite fails intermittently when
the full test suite is run, but passes when run alone. Observed on
`test_explored_equals_length_plus_one_on_wide_shapes[8]`: the resolver
explores more than `max_visited=1000` shapes and raises `ResolverError`.
Likely an execution-order or budget-edge issue, not a logic bug.

**Minimal example.** `pytest tests/ resolver/tests/` sometimes shows
one failure; `pytest resolver/tests/test_resolver.py` alone passes.

**Status.** open.

**Notes.** Originally recorded as "asymmetry of
structural_distance_numbers", with example
`(30030, 2) = 7` vs `(2, 30030) = 5`. Re-verified on 14 cases: the
distance is symmetric. The original failing example does not reproduce.
The real issue is test flakiness under the full suite, unrelated to
symmetry.

### T18 — Resolver satellite has open lint and type issues

**Statement.** Adding `resolver/` to the CI's ruff and mypy checks
surfaces ~50 ruff errors and ~16 mypy errors. Representative cases:

- ruff: `__all__` not sorted, `×` (MULTIPLICATION SIGN) in strings and
  docstrings flagged as ambiguous, `zip` without `strict=`, unused
  imports, unused unpacked variables, `typing.Iterator` instead of
  `collections.abc`.
- mypy: `petra` lacks a `py.typed` marker, `struct_destruct.py:160`
  redefines `results`.

**Status.** open.

**Notes.** CI currently installs `resolver` (so its tests run) but
does not lint or type-check it. To close T18, either fix the issues or
add explicit excludes to the CI config.

### T19 — Asymptotic form of stab(N)

**Statement.** Decide between
`stab(N) = a + b/log N` with `a ~ 13` and
`stab(N) = c/(log N)^alpha` with `alpha ~ 0.15`,
where `stab(N)` is the percentage of `n in [1, N-1]` such that
`g(n+1) = g(n)`, with `g` the arithmetic recurrence of T16.

**Minimal example.** The local slope of `stab * log N` versus `log N`
is `12.75, 15.14, 13.50, 13.47, 13.25, 13.09` for
`N = 10^2, 10^3, 10^4, 10^5, 10^6, 10^7, 10^8`. It decreases
monotonically over the last four decades but has not stabilised.

**Status.** open.

**Depends on.** T16 (reduction to `g`).

**Notes.** `10^8` is the practical limit of the linear-sieve method
(~ 40 s sieve, ~ 132 s recurrence, ~ 800 MB peak). Distinguishing (A)
from (B) probably requires either a larger scale with a segmented
sieve, or an analytic argument on the exponent multisets of
consecutive integers.

## Notes on the list

