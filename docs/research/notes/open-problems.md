# Open problems

Status: living document
Scope: active research directions, restated as concrete problems
Update rule: append new problems, update status, never delete

This file replaces the T-series as the front of the research line.
`open-threads.md` stays as historical archive. Every problem below
points to the notes that motivate it.

Format:

- **Statement.** One sentence.
- **Why now.** Which observation makes this answerable today.
- **First step.** The smallest concrete thing to do.
- **Status.** open / in progress / blocked / closed.

## P1 — Family separation in shape space

**Statement.** At which size do the families Perfect, Primorials,
Hamming, HighlyComposite separate in PETRA shape space, with what
margin, and where do they overlap?

**Why now.** `pet-problem-statement.md` states the question but has
never been closed. The distance atlas and the fingerprint layer
already exist. The families are computable. Nothing new is needed
except running the measurement.

**First step.** Build the four families up to a fixed bound, compute
pairwise structural distances, report the confusion matrix between
intra-family compactness and inter-family separation.

**Status.** closed.

**Result.** Negative. `docs/reports/generated/families-benchmark-disjoint.md`
records a bounded benchmark on disjoint samples of the four families
(Perfect 4, Primorials 6, Hamming 28, HighlyComposite 26), under both
`distance` and `structural_distance`. PET does not produce hard
separation under the strict gap test. Perfect is the tightest family
(structural diameter 2.00); HighlyComposite the widest. The strongest
average separation is Perfect vs HighlyComposite. Perfect and Hamming
reach structural distance 0.00 on at least one pair.

The question is closed. Larger samples would only confirm the negative,
and Perfect numbers are too rare to enlarge the sample meaningfully.

## P2 — Collatz reduction dominance: explanation or counterexample

**Statement.** Collatz is reduction-dominant (56.7-59.4% reduction,
stable across scales). No other tested map shares the profile. Why?
And is Collatz the only map with this property, or a counterexample
exists?

**Why now.** `arithmetic-maps-structural-fingerprint.md` records the
observation with five starting values and eight control maps. The
observation is solid. The explanation is missing.

**First step.** Extend the tested map set to cover the space of
Collatz-like maps (3n+k, k odd), and check whether reduction dominance
correlates with any known property of the map.

**Status.** in progress.

**First result.** The original claim ("Collatz is the only
reduction-dominant map in the tested set") is refuted. Every tested
`3n+k` (k odd) is reduction-dominant, with margins between +14 and +25
points. The distinction is not Collatz vs everything else, it is
`3n+k` vs linear maps. Recorded in
`collatz-like-reduction-dominance.md`. The original note has been
corrected.

**Closed.** The counterexample is the result. The follow-up question
("why does the factor 3 reduce and the factor 2 not?") is out of
scope for PETRA: it is an arithmetic question about values, not a
structural question about shapes. PETRA observes maps through shape
conversion; it does not define them. The question is not pursued
here.

## P3 — Minimal context for deterministic succession

**Statement.** The shape of `n` does not determine the shape of the
Collatz successor. Shape plus `n mod 2^k` does. What is the minimal
`k`? Constant or growing with `n`?

**Why now.** T09 states the observation but does not quantify the
context. The question is a yes/no with a computable answer.

**First step.** For each `n` up to a bound, find the smallest `k` such
that `(shape(n), n mod 2^k)` determines `shape(Collatz(n))`. Report
the distribution of minimal `k`.

**Status.** closed.

**Result.** Negative. No bounded `k` is universal. By Dirichlet's
theorem, for every `k` there are infinitely many primes in the same
residue class `mod 2^k`; they share the same shape (`○^(A)`) but their
images under `3n+1` have different shapes. The smallest explicit
counterexample is at `k = 3`, among primes `≡ 5 mod 8`. Recorded in
`shape-context-not-bounded.md`.

## P4 — Loss from factorization to shape

**Statement.** The shape `○^(A × B)` does not distinguish `2×3` from
`3×5`. How many integers share a given shape, and how does that count
grow with the shape?

**Why now.** This is the cost of the shape abstraction, and it has
never been measured. The answer is arithmetic, but it comes directly
from the PETRA construction boundary.

**First step.** For shapes up to `node_count = 15`, count the number of
integers `n <= N` that realize each shape, for increasing `N`. Report
the growth rate per shape.

**Status.** closed.

**Result.** Negative. The shape is a coarse descriptor: many integers
share the same shape. At `N = 10000`, only 64 distinct shapes exist,
and the top 10 shapes cover 92.7% of the integers. The most frequent
shape is always `○^(A × B)` (semiprimes with distinct primes), growing
roughly linearly with `N`. Recorded in `shape-multiplicity.md`.

## P5 — Symmetric struct/destruct

**Statement.** Today `struct` adds fathers only at the root (via
`append` and `prepend`) or replaces a leaf with a container (via
`replace`). It does not add a father to an inner container. As a
result, `destruct` can produce a `(piece, rest, kind)` that
`struct(rest, piece)` does not invert (seen for `12^3`,
`t01-struct-destruct-exponential.md`).

Two phases:

- **A.** Extend `struct` with a fourth hook: add a father to a
  container at a given path inside the shape.
- **B.** Verify whether, with the extension, every
  `(piece, rest, kind) in destruct(s)` satisfies `s in struct(rest, piece)`.

**Why now.** The limit was found while closing T01. The exact shape of
the limit is known, and the fix is local.

**First step.** Implement the fourth hook, then re-run the four pairs
from `t01_exponential_struct_destruct.py` and check phase B on each.

**Status.** closed.

**Result.** Positive on the tested cases. Phase A: `struct` gains a
keyword `inner: bool = False`. Phase B: with `inner=True`, every
destruct case is recomposed on the four tested pairs (12^3, 30^2,
30^3, 6^4) and on six additional shapes (14 tests pass). The limit
found in T01 is resolved. Recorded in
`p5-symmetric-struct-destruct.md`.

## P6 — Functoriality of the fingerprint

**Statement.** For which transformations `T` on sequences does there
exist a map `F_T` such that
`fingerprint(T(f)) = F_T(fingerprint(f))`?

**Why now.** `fingerprint.py` exposes the fingerprint as a measurement.
The classes it produces on `base^n` seem to follow the shape of the
base, not the value. Whether `T` composes cleanly on top of that is
untested.

**First step.** For each candidate `T` (shift, double, scaling,
reversal), check on a bounded sample whether bases in the same
fingerprint class stay in the same transformed class.

**Status.** in progress.

**Partial result.** For `shift` and `double`, on bases `b in [2, 40]`
and `N = 60`, the map `F_T` exists on the sample. The fingerprint
classes appear to follow `shape(base)`. Recorded in
`t02-functoriality-partial.md`. General question open.

## P7 — Multiset-of-exponents invariant

**Statement.** Does `fingerprint(k^n)` depend only on the multiset of
exponents in `k`, not on the numeric values of the primes nor on their
order?

**Why now.** The exact identity in
`exponential-base-structural-class.md` already answers this.

**Status.** closed.

**Result.** Positive. The identity removes the prime values from the
shape. `node_count` is symmetric under reordering of terms, so the
fingerprint is order-invariant. The multiset `{e1, ..., er}` is the
only surviving input. Verified on pairs `(12, 18)` and `(60, 90)`.
Recorded in `t03-multiset-invariant.md`.

## P8 — Meet/join as clustering tools

**Statement.** Use meet and join to cluster shapes by structural
similarity, via `overlap = node_count(meet) / node_count(join)`.

**Why now.** The tool exists (`resolver.structural_algebra`), the
application was never tested.

**Status.** closed.

**Result.** Negative. On `N = 500` (124251 pairs), the overlap takes
only 17 distinct values, and the top 6 cover 83% of the pairs. It is
too coarse to discriminate. Recorded in
`t04-overlap-too-coarse.md`.

## P9 — Arithmetic layer above the Resolver

**Statement.** Build a class that keeps `(shape, key)` together and
supports arithmetic operations on the pair.

**Why now.** Thread T05 proposed this. It predates the shape-first
consolidation.

**Status.** closed (out of scope).

**Result.** Not pursued. PETRA is shape-first; the value does not
appear in the shape by construction. A `(shape, key)` pair restores
the value and reintroduces arithmetic at the core of the object
model. The proposed operators (`12 / 3 = 4`) are not general: they
work only when the arithmetic operation has a structural counterpart.
An arithmetic layer is a possible external application of PETRA, not
an extension of it.

## P10 — Structural elision as p/p = 1

**Statement.** Given two indistinguishable leaf fathers in a
container, eliding one returns a unique reduced shape. Tracking
*which* one was elided requires a key.

**Why now.** Thread T06 proposed this, as a companion to T05.

**Status.** closed (out of scope).

**Result.** Not pursued. Same scope argument as P9. SHED already
elides a leaf father, and the reduced shape is unique. The ambiguity
is only in tracking the removed leaf, which requires a key and
reintroduces arithmetic. PETRA does not carry persistent identities
between terms; two leaves are the same thing. History is not
structure.

## P11 — Finer structural metrics in the fingerprint

**Statement.** Replace `node_count` with a finer measure (depth,
depth_mass, deep_branches) in the fingerprint and test whether the
classification of bases changes.

**Why now.** Thread T07 proposed this. The fingerprint layer already
exists; only the metric needs to be swapped.

**Status.** closed.

**Result.** Positive. With `depth` and `depth_mass`, base 12
separates from the other eight tested bases at `N = 60`. With
`node_count`, all nine share one class. With `deep_branches`, all
nine collapse to a single class. The metric choice is not neutral.
Recorded in `t07-finer-metrics-change-classification.md`.

## P12 — Reduction profile of 3n-1

**Statement.** Is the reduction profile of Collatz (`3n+1`)
invariant under the mirror map `3n-1`?

**Why now.** P2 showed all `3n+k` (k odd) are reduction-dominant.
`3n-1` is the case `k = -1`. The tool exists.

**Status.** closed.

**Result.** Positive. `3n-1` is reduction-dominant, same profile as
`3n+k` (k > 0). Five starting values tested, margins between +13 and
+20 points. The sign of `k` does not matter; the factor 3 does.
Recorded in `t08-3n-minus-1.md`.

## P13 — Fingerprint catalogue

**Statement.** Build a catalogue of fingerprints for known sequence
families and use it to classify novel sequences.

**Why now.** Thread T10 proposed this.

**Status.** closed (out of scope).

**Result.** Not pursued. Two reasons: `fingerprint.py` handles only
`base^n`, not arbitrary sequences; the fingerprint is window-dependent
and not a class invariant, so a catalogue would have no stable
entries. P1 also showed that integer families do not separate in shape
space.

## P14 — Beatty sequences and non-obvious families

**Statement.** Test the fingerprint classifier on Beatty sequences,
sums of two squares, random walks with drift.

**Why now.** Thread T11 proposed this.

**Status.** closed (out of scope).

**Result.** Not pursued. Depends on a fingerprint classifier that
does not exist, and on the assumption that families separate in
shape space, which P1 falsified.

## P15 — Invariance under sparse sampling

**Statement.** Test whether the fingerprint of a sequence changes when
sampled every k-th term.

**Why now.** Thread T12 proposed this.

**Status.** closed (out of scope).

**Result.** Not pursued. Depends on a fingerprint for arbitrary
sequences, which does not exist.

## P16 — Distribution of overlap in a range

**Statement.** Compute the distribution of `overlap(a, b)` across all
pairs in a range.

**Why now.** Thread T13 proposed this.

**Status.** closed (covered by P8).

**Result.** Negative. Same as P8: 17 distinct values on `N = 500`,
top 6 covering 83% of pairs.

## P17 — Fingerprint of a Collatz trajectory

**Statement.** Treat a Collatz trajectory as a sequence and compute
its fingerprint.

**Why now.** Thread T14 proposed this.

**Status.** closed (out of scope).

**Result.** Not pursued. Depends on a fingerprint for arbitrary
sequences, which does not exist.

## P18 — Structural signature of prime gaps

**Statement.** Compute the structural fingerprint of the prime gaps.

**Why now.** Thread T15 proposed this.

**Status.** closed (out of scope).

**Result.** Not pursued. Same limitation as T10, T11, T12, T14: no
fingerprint for arbitrary sequences exists.

## P19 — Asymptotic form of stab(N)

**Statement.** Determine the asymptotic behaviour of
`stab(N) = #{ n in [1, N-1] : g(n+1) = g(n) } / (N-1)`.

Two open points:

1. Does `rho(N)` converge, and to which value?
2. How does `SumPk2(N)` behave asymptotically?

**Why now.** Thread T19, downstream of T16. The reduction to the
arithmetic function `g` is exact; only the asymptotics is missing.

**Status.** in progress.

**Result.** Fifth data point at `N = 10^8` excludes the hypothesis
`SumPk2 ~ c / sqrt(log log N)`: the product `SumPk2 * sqrt(log log N)`
continues to decline (33.49, 32.96, 32.62, 32.38, 32.19). A five-point
fit gives `alpha ~ 0.51`. `rho` continues to increase slowly
(0.7595 to 0.806). `stab` continues to decrease (17.07 to 15.20).
Recorded in `t19-stab-fifth-point.md`.

Going beyond `10^8` requires a segmented sieve or an analytic
argument on exponent multisets of consecutive integers.

## P20 — Cache by id() in the resolver search

**Statement.** The A* search cached per-shape metrics by `id(shape)`.
`id` is unique only among live objects, so discarded shapes could have
their `id` reused and poison the cache, corrupting the heuristic.

**Why now.** Thread T17 observed intermittent test failures only under
the full suite. Root cause identified.

**Status.** closed.

**Result.** Fixed. Cache keyed by `shape` instead of `id(shape)` in
`_build_cached_metrics`. Verified: 500 isolated runs of the failing
case give the correct path length only; full suite passes 718/718 for
10 consecutive runs. Recorded in `t17-cache-id-bug.md`.

