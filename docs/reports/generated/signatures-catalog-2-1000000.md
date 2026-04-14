# PET structural signatures catalog (2..1000000)

## Scope

This document proposes a compact descriptive vocabulary for PET structural signatures
based on bounded evidence from the scan range `2..1000000`.

It focuses on reusable signature components that already appear in the codebase or
in bounded empirical reports: structural shape, branch profile, profile shape,
height, maximum branching, recursive mass, and minimal realizer.

The goal is descriptive stability, not complete classification.

## Reproduction

### Command

    python3 -m src.pet.cli scan 2 1000000 --jsonl docs/reports/data/scan-2-1000000.jsonl

### Input basis

This catalog is based on bounded evidence from the scan dataset
`docs/reports/data/scan-2-1000000.jsonl`.

It also consolidates stable signature components already reused in current PET
reports and code-facing descriptors.

## Proposed signature vocabulary

A practical PET structural signature can be described by the tuple

`(shape, branch_profile, profile_shape, height, max_branching, recursive_mass)`.

- `shape` is the full prime-free rooted structure.
- `branch_profile` records the number of nodes at each depth level.
- `profile_shape` is a compact morphological classifier (`point`, `linear`, `normal`, `expanding`, `bell`).
- `height`, `max_branching`, and `recursive_mass` provide stable scalar descriptors.
- the minimal realizer of a signature component is the smallest `n` in the bounded scan where that component first appears.

## Representative signatures and minimal realizers

A first compact catalog can start from stable components already observed in bounded scans.

| component | signature value | minimal realizer |
|---|---|---:|
| `profile_shape` | `point` | 2 |
| `profile_shape` | `linear` | 4 |
| `profile_shape` | `normal` | 12 |
| `profile_shape` | `expanding` | 64 |
| `profile_shape` | `bell` | 4096 |
| `recursive_mass` | `0` | 2 |
| `recursive_mass` | `1` | 4 |
| `recursive_mass` | `2` | 16 |
| `recursive_mass` | `3` | 144 |
| `recursive_mass` | `4` | 1296 |
| `recursive_mass` | `5` | 32400 |
| `recursive_mass` | `6` | 810000 |

## Stability notes

The components above are relatively stable because they already have explicit operational meaning in the current codebase and reports.

`branch_profile`, `profile_shape`, `height`, `max_branching`, and `recursive_mass` are usable descriptive components today.
The full `shape` is also stable as a prime-free rooted structure, but its human-facing naming scheme is not yet standardized.

Minimal realizers in this document are bounded empirical minima within `2..1000000`.
They should be treated as reproducible observations, not as proofs of global minimality beyond the scanned range.

## Transition-law note

A further bounded empirical result is that elementary transitions between PET
generator families behave deterministically in the tested range.

Checked setup:
- source values: `2..100000`
- tested primes for local moves: `2, 3, 5, 7, 11, 13, 17, 19, 23, 29`

Observed bounded laws:

### 1. `T_new(g)`

If a number in generator family `g` is multiplied by a **new prime** not already
present in its factorization, the target generator family is determined only by `g`.

Examples:
- `2 -> 6`
- `6 -> 30`
- `30 -> 210`
- `60 -> 420`
- `210 -> 2310`

### 2. `T_inc`

For exponent-increase moves with an **existing prime**, the coarse bounded law
`(g, e) -> g'` is deterministic in the tested range.

A stronger bounded compression also holds for `e >= 2`:

`T_inc ~ (g, gen(e), gen(e+1))`

Observed counts:
- raw classes `(g, e)`, `e >= 2`: `142`
- compressed classes `(g, gen(e), gen(e+1))`: `122`
- non-deterministic compressed classes: `0`

So the currently strongest bounded empirical formulation is not just
`T_inc(g, e)`, but the refined local-generator law above.

### 3. `T_drop(g)`

If a prime factor of exponent `1` is removed, the source generator family `g`
moves to a target family determined only by `g`.

Examples:
- `6 -> 2`
- `30 -> 6`
- `210 -> 30`
- `420 -> 60`
- `2310 -> 210`

### 4. `T_dec`

For exponent-decrease moves on an **existing prime**, the coarse bounded law
`(g, e) -> g'` is deterministic in the tested range.

A stronger bounded compression also holds for `e >= 3`:

`T_dec ~ (g, gen(e), gen(e-1))`

Observed counts:
- raw classes `(g, e)`, `e >= 3`: `116`
- compressed classes `(g, gen(e), gen(e-1))`: `100`
- non-deterministic compressed classes: `0`

So the currently strongest bounded empirical formulation is not just
`T_dec(g, e)`, but the refined local-generator law above.

### Equivalent coordinate reformulation

Let `h = gen(n / p^e)` be the generator of the ambient part left after removing
the moved prime power.

Then the same bounded laws can be rewritten as:

- `T_inc ~ (h, gen(e), gen(e+1))`
- `T_dec ~ (h, gen(e), gen(e-1))`

In the tested range this is **not** a stronger law, only an equivalent change of
coordinates: once `gen(e)` is fixed, `(g, gen(e))` and `(h, gen(e))` determine
each other, and the compressed class counts stay the same.

### Failed stronger compressions

The following stronger compressions were tested in the same bounded range and
failed:

- unordered local pair `{gen(e), gen(e±1)}`
- edge-factor laws of the form `g'/g = rho(...)`
- centered local windows `(gen(e-1), gen(e), gen(e+1))`
- local multiplicity augmentations using exponent-count data

### Bounded determinism status

Observed checks:
- non-deterministic `T_new` classes: `0`
- non-deterministic coarse `T_inc(g, e)` classes: `0`
- non-deterministic pair-compressed `T_inc` classes: `0`
- non-deterministic `T_drop` classes: `0`
- non-deterministic coarse `T_dec(g, e)` classes: `0`
- non-deterministic pair-compressed `T_dec` classes: `0`

This should currently be treated as a bounded empirical pattern, not as a theorem.

## Observations

1. The catalog does not attempt a full taxonomy of all PET forms; it isolates a
   compact subset of signature components that already have stable descriptive use.

2. `profile_shape`, `height`, `max_branching`, and `recursive_mass` already form
   a practical bounded vocabulary for comparing PET structures across reports.

3. Minimal realizers listed here are bounded empirical first occurrences within
   `2..1000000`, so they are useful as reproducible reference points but not as
   global minimality claims.

## Limits

This catalog is descriptive and bounded.

It does not claim a complete classification of PET forms, a final naming system for all shapes,
or global minimality results beyond the scanned range.
