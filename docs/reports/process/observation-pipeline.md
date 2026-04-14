# PET observation pipeline

## Scope

This document defines a lightweight vocabulary for PET findings so that reports and notes can distinguish bounded observations from stronger claims.

## Vocabulary

### Observation

A reproducible statement tied to explicit data, examples, or a bounded scan.

Example:
- in `2..10000`, the first record with maximum observed height is `16`

### Bounded empirical pattern

A reproducible regularity seen across an explicit bounded dataset, without claiming it continues beyond that range.

Example:
- in `2..1000000`, height `4` remains rare

### Conjecture

A claim believed to extend beyond the scanned range, but not yet established.

Example:
- the PET shape catalog continues to expand for all sufficiently large bounds

### Established statement

A statement justified by proof, direct definition, or already-settled implementation semantics.

Example:
- `recursive_mass(tree) == 0` iff the PET is squarefree under the current PET definitions

## Promotion rules

- observation -> bounded empirical pattern: requires repeated reproducible evidence across a stated bounded range
- bounded empirical pattern -> conjecture: requires an explicit beyond-range claim stated as unproven
- conjecture -> established statement: requires proof or direct definitional status
- no report should silently promote a bounded finding into a general claim

## First classified PET examples

| statement | class |
|---|---|
| In `2..10000`, height `1` or `2` accounts for `9559 / 9999` records. | observation |
| In `2..1000000`, height `4` remains rare. | bounded empirical pattern |
| PET shape discovery continues indefinitely. | conjecture |
| `profile_shape(tree)` is one of `point`, `linear`, `normal`, `expanding`, `bell`. | established statement |

## Usage rule

Reports should label bounded results descriptively and avoid theory language unless a statement is explicitly marked as a conjecture or established statement.
