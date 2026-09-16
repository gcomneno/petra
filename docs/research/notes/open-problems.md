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

**Status.** open.

## P3 — Minimal context for deterministic succession

**Statement.** The shape of `n` does not determine the shape of the
Collatz successor. Shape plus `n mod 2^k` does. What is the minimal
`k`? Constant or growing with `n`?

**Why now.** T09 states the observation but does not quantify the
context. The question is a yes/no with a computable answer.

**First step.** For each `n` up to a bound, find the smallest `k` such
that `(shape(n), n mod 2^k)` determines `shape(Collatz(n))`. Report
the distribution of minimal `k`.

**Status.** open.

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

**Status.** open.
