# Open research threads

**Front.** The active front is now `open-problems.md`. This file is kept as historical archive.


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

### T01 — Composition and decomposition of shape(k^n)

**Statement.** The exact identity `shape(k^n) = C(r0^shape(e1*n), ...)`
is proven. Use `struct` and `destruct` to explore the exponential case
`k^n` through composition and decomposition.

**Minimal example.** Decompose `shape(k^n)` for small `k` and `n`, and
see what pieces appear.

**Status.** closed.

**Notes.** Earlier results of the T01 line are recorded elsewhere and
are not part of this thread:

- exact identity and duplication lemma: `exponential-base-structural-class.md`;
- recursive reconstruction: `recursive-reconstruction-t01.md`;
- cumulative fingerprint convergence: moved to T16;
- asymmetry of `structural_distance`: closed as T17 (test flakiness).

The exponential case is explored in
`t01-struct-destruct-exponential.md`: struct/destruct work on
`shape(k^n)` with one limit (fathers of inner containers are not
recomposed by `struct`), and the duplication lemma is verified.
The canonicity of the reconstruction chain is left open in the
`recursive-reconstruction-t01.md` note; not tracked as a thread.

**Forward.** Prerequisite for T02 (functor).

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

**Status.** closed (out of scope).

**Notes.** PETRA is shape-first: the value does not appear in the
shape, by construction (SPEC §1.2, and the exact identity in
`exponential-base-structural-class.md`). A `(shape, key)` pair that
restores the value reintroduces arithmetic at the core of the object
model. Division `12 / 3 = 4` works only when the divisor divides the
dividend; the operator is not general. The thread predates the
shape-first consolidation. It is a possible external application of
PETRA, not an extension of PETRA.

### T06 — Structural elision as p/p = 1

**Statement.** Given `shape(p) and shape(p)` in a common context,
structural elision returns Leaf. Ambiguity arises when terms are
indistinguishable without a key.

**Status.** closed (out of scope).

**Notes.** Same scope argument as T05. SHED (canonical width
removal) already elides a leaf father. The reduced shape is unique.
What is not determined is which leaf was removed when several are
indistinguishable, and that requires a key. A key reintroduces
arithmetic in the object model. PETRA does not carry persistent
identities between terms; two leaves are the same thing. Tracking
which one was elided is history, not structure.

### T07 — Finer structural metrics

**Statement.** Replace `node_count` with a finer measure (depth-weighted
mass, recursive mass, canonical form length) and test whether the
fingerprint classification changes.

**Minimal example.** Two shapes with the same node_count but different
depths might produce different fingerprints under a depth-weighted
metric.

**Status.** closed.

**Result.** Positive. Replacing `node_count` with `depth` or
`depth_mass` in the fingerprint changes the classification: base 12
separates from the other tested bases. `deep_branches` is too coarse.
Recorded in `t07-finer-metrics-change-classification.md`. The
earlier note `recursive-metric-no-clusters.md` addressed a different
question (a distance, not a fingerprint).

### T08 — Collatz on `3n - 1`

**Statement.** Test whether the Collatz reduction profile is invariant
under the mirror map `3n - 1`. The `3n - 1` map has three known cycles,
so the results may differ substantially.

**Minimal example.** Start at 5 under `3n - 1`.

**Status.** closed.

**Result.** Positive. `3n-1` is reduction-dominant, same profile as
`3n+k` (k odd, k > 0). Five starting values tested, all with
`red > exp`. The sign of `k` does not matter. Recorded in
`t08-3n-minus-1.md`.

### T09 — Shape-plus-context for deterministic succession

**Statement.** A pure shape does not determine the Collatz successor.
A shape together with `n mod 2^k` (for sufficient k) does. Explore
whether this "shape-plus-context" state recovers a ranking function.

**Minimal example.** `6` and `15` share a shape; `6 mod 4 = 2`,
`15 mod 4 = 3`. The two residues have different Collatz successors.

**Status.** closed (covered by P3).

**Result.** Negative. No bounded `k` is universal. See
`shape-context-not-bounded.md`.

### T10 — Fingerprint catalogue

**Statement.** Build a catalogue of fingerprints for many known
sequence families. Use it to assign novel sequences to families.

**Status.** closed (out of scope).

**Notes.** Two independent reasons:

- `fingerprint.py` computes the fingerprint of `base^n`, not of an
  arbitrary sequence. A catalogue for Fibonacci, Beatty, or prime
  gaps would need a different fingerprint, which does not exist.
- The fingerprint is window-dependent and not a class invariant
  (`exponential-base-structural-class.md`, both conjectures
  falsified). A catalogue built on a non-invariant has no stable
  entries.

Additionally, P1 showed that classical integer families do not
separate in shape space. Even if the catalogue existed, it would not
discriminate.

### T11 — Beatty sequences and other non-obvious families

**Statement.** Test the fingerprint classifier on families not
generated by recurrences or algebraic formulas: Beatty sequences,
sums of two squares in enumeration order, random walks with drift.

**Status.** closed (out of scope).

**Notes.** The thread presupposes a fingerprint classifier, which
does not exist: `fingerprint.py` handles only `base^n`. T10 (P13) was
closed for the same reason. P1 showed that even with a classifier,
integer families do not separate in shape space. T11 inherits all
three limitations.

### T12 — Invariance under sparse sampling

**Statement.** Test whether the fingerprint of a sequence changes when
sampled sparsely (every second term, every k-th term).

**Status.** closed (out of scope).

**Notes.** Same reason as T10 and T11: the thread presupposes a
fingerprint for arbitrary sequences, which does not exist.
`fingerprint.py` handles only `base^n`. Sparse sampling of an
arbitrary sequence cannot be measured.

### T13 — Distribution of overlap in a range

**Statement.** Compute the distribution of `overlap(a, b)` across all
pairs in a range.

**Status.** closed (covered by P8).

**Result.** Negative. On `N = 500` (124251 pairs), the overlap takes
only 17 distinct values, and the top 6 cover 83% of the pairs. It is
too coarse to discriminate. See `t04-overlap-too-coarse.md`.

### T14 — Fingerprint of Collatz trajectory itself

**Statement.** Treat the Collatz trajectory from a given start as a
sequence of values and compute its fingerprint.

**Status.** closed (out of scope).

**Notes.** Same limitation as T10, T11, T12: `fingerprint.py` handles
only `base^n`. A fingerprint for an arbitrary sequence (like a Collatz
trajectory) does not exist.

### T15 — Structural signature of prime gaps

**Statement.** Take the sequence of prime gaps and compute its
structural fingerprint.

**Status.** closed (out of scope).

**Notes.** Same limitation as T10, T11, T12, T14: no fingerprint for
arbitrary sequences exists. `fingerprint.py` handles only `base^n`.

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

**Statement.** Determine the asymptotic behaviour of

    stab(N) = #{ n in [1, N-1] : g(n+1) = g(n) } / (N-1),

where `g` is the arithmetic recurrence of T16. The exact decomposition
`stab(N) = rho(N) * SumPk2(N)` holds by definition, where
`SumPk2(N) = sum_k p_k(N)^2` is the empirical collision probability
of `g(n)` and `rho(N)` is the correlation factor between `g(n)` and
`g(n+1)`. The open problems are:

1. Does `rho(N)` converge, and if so, to which value?
2. How does `SumPk2(N)` behave asymptotically?

**Minimal example.** Measured values:

| N | stab | SumPk2 | rho |
| ---: | ---: | ---: | ---: |
| 10^4 | 17.07 | 22.48 | 0.7595 |
| 10^5 | 16.36 | 21.09 | 0.7758 |
| 10^6 | 15.88 | 20.13 | 0.7888 |
| 10^7 | 15.50 | 19.42 | 0.7983 |

`SumPk2` decreases by about 5% per decade; `rho` increases by about
5% per decade; the increments of `rho` shrink (`+0.0163`, `+0.0130`,
`+0.0095`). The product `stab` decreases only by about 9% over three
decades.

**Status.** open.

**Depends on.** T16 (reduction to `g`).

**Notes.** The two earlier candidate forms
`stab(N) = a + b/log N` and `stab(N) = c/(log N)^alpha` are both
incompatible with the data: `SumPk2` is not constant, and its
estimated exponent in `log log N` decreases from 1.87 to 1.60 without
stabilising.

A fifth data point at `N = 10^8` was computed with
`tools/research/t16_asymptotics.py`. It excludes the hypothesis
`SumPk2 ~ c / sqrt(log log N)`: the quantity `SumPk2 * sqrt(log log N)`
continues to decline (33.49, 32.96, 32.62, 32.38, 32.19 over five
decades), giving a five-point fit `alpha ~ 0.51`. `rho` continues to
increase slowly (0.7595, 0.7758, 0.7888, 0.7983, 0.806). `stab`
continues to decrease (17.07, 16.36, 15.88, 15.50, 15.20). Two open
points remain. Recorded in `t19-stab-fifth-point.md`.

A segmented sieve or an analytic argument on exponent multisets of
consecutive integers is required to go beyond `10^8`.

## Notes on the list

