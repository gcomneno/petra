# PET metrics first-principles audit

<!-- PETRA-HISTORICAL-FOUNDATION -->
> [!IMPORTANT]
> **Historical PET/PET-PEG design material.** This document does not define PETRA. Use [`../reference/SPEC.md`](../reference/SPEC.md) as the sole canonical specification.


This document audits `src/pet/metrics.py` against the current first-principles
PET model and the stable PET-Base canonical metrics.

The goal is classification and semantic clarity, not refactoring.

This audit does not change implementation behavior.

## Audit basis

This audit is based on:

- `src/pet/core.py`
- `src/pet/metrics.py`
- `src/pet/object_metrics.py`
- `docs/reference/SPEC.md`
- `docs/foundations/pet-notation-collapse.md`
- `docs/foundations/pet-first-principles-implementation-audit.md`
- `docs/foundations/pet-module-stability-classification.md`

## First-principles reference points

The first-principles model defines:

- `PET(1)` as the recursive leaf object
- `support(P)` as the current-level prime-root set
- `height(1) = 0`
- `height(P) = 1 + max(height(E_i))` for compound PET objects
- numeric collapse as recursive evaluation of exponent objects
- the construction boundary: PET notation does not hide factorization cost

Important boundary:

`support(P)` is current-level support only.

It does not automatically include prime roots inside exponent objects.

## Stable PET-Base metric contract

The stable PET-Base metric contract is implemented in `src/pet/core.py`.

The canonical metrics are:

- `node_count(tree)`
- `leaf_count(tree)`
- `height(tree)`
- `max_branching(tree)`
- `branch_profile(tree)`
- `recursive_mass(tree)`
- `average_leaf_depth(tree)`
- `leaf_depth_variance(tree)`

These are exposed through:

- `metrics_dict(tree)`
- `pet metrics`
- scan JSONL records

The stable tree/JSON representation currently targets PET-Base documents for
`N >= 2`.

In this representation, exponent leaf `1` is represented as `None` in Python and
as JSON `null` in canonical JSON.

## Object-native metric bridge

`src/pet/object_metrics.py` computes legacy-compatible metrics directly from
`PETObject`.

This matters because the object-native layer supports `pet_object_from_int(1)`.

The object metric bridge aligns with the first-principles convention:

    height(PET(1)) = 0

because `pet_object_height(...)` returns `0` when there are no metric roots.

This makes `object_metrics.py` the cleanest bridge between:

- first-principles `PET(1)` semantics
- legacy-compatible metric names
- PET/PEG 2.0 object-native structure

## `metrics.py` classification

`src/pet/metrics.py` does not define the canonical PET-Base metric contract.

It defines extended metrics, derived classifiers, and research/reporting helpers
on top of canonical PET-Base trees.

Most functions in `metrics.py` call `validate(tree)` and then reuse canonical
metrics from `core.py`.

Therefore, they inherit the current stable PET-Base tree domain and its `N >= 2`
machine-facing representation boundary.

## Function-level audit

| Function | Classification | Depends on | First-principles relationship | Recommendation |
|---|---|---|---|---|
| `verticality_ratio(tree)` | extended metric | `height`, `node_count` | Derived from legacy-compatible height. It is meaningful for PET-Base trees, but inherits the `N >= 2` tree domain. | Keep extended/research. Do not promote to canonical default without separate admission review. |
| `structural_asymmetry(tree)` | extended metric | `branch_profile` | Measures profile variance across levels. It does not correspond directly to first-principles `support(P)`. | Keep extended/research. Useful for shape analysis. |
| `subtree_mixing_score(tree)` | research metric | `pet.algebra._shape` | Research helper for local subtree-shape mixing. It is not a first-principles concept. | Keep research-only. Do not promote without separate proof of value and stable definition. |
| `has_root_mixed_simple_pattern(tree)` | research helper | `pet.algebra._shape` | Root-shape pattern detector. It is not a first-principles concept and is tied to a specific research pattern. | Keep research-only. |
| `extended_metrics(tree)` | aggregation helper | `metrics_dict` plus extended metrics | Combines canonical metrics and research metrics in one dictionary. | Useful, but output should not be confused with canonical `metrics_dict`. |
| `is_linear(tree)` | derived classifier | `max_branching` | Shape classifier over canonical PET-Base trees. Documented in `SPEC.md`. | Keep as derived classifier, not a metric primitive. |
| `is_level_uniform(tree)` | derived classifier | `branch_profile` | Shape classifier over branch-profile structure. Documented in `SPEC.md`. | Keep as derived classifier. |
| `is_expanding(tree)` | derived classifier | `branch_profile` | Shape classifier for widening profiles. Documented as rare/empirical in `SPEC.md`. | Keep as derived classifier with empirical caution. |
| `is_squarefree(tree)` | derived classifier | `recursive_mass` | Detects no recursive exponent structure in PET-Base trees. Related to all exponents being leaf `1`. | Keep as derived classifier. |
| `leaf_ratio(tree)` | extended metric | `leaf_count`, `node_count` | Ratio over legacy-compatible PET-Base tree nodes/leaves. It is not first-principles support. | Keep extended/reporting. |
| `profile_shape(tree)` | morphology classifier | `branch_profile` | Coarse classifier over branch-profile shape. Not a first-principles primitive. | Keep reporting/research-facing. |

## Height semantics

There are two compatible but distinct height contexts:

1. First-principles object height
2. Legacy-compatible PET-Base tree height

First-principles height defines:

    height(1) = 0

and:

    height(P) = 1 + max(height(E_i))

for compound PET objects.

Legacy PET-Base tree height in `core.py` starts from valid non-empty PET trees.
For example, a prime tree has height `1`.

This is compatible with first-principles height for `PET(n)` where `n >= 2`.

The important distinction is that `core.py` does not expose a standalone tree
for `PET(1)`.

Therefore:

- `core.height(tree)` is canonical for current PET-Base trees
- `pet_object_height(obj)` is the better bridge for `PET(1)`
- `metrics.py` inherits `core.height(tree)` semantics

## Support semantics

First-principles support is:

    support(P) = current-level prime roots of P

`metrics.py` currently does not define a `support(P)` function.

Some functions use `branch_profile`, `recursive_mass`, `leaf_count`, or shape
helpers, but none of them should be treated as first-principles support.

In particular:

- `branch_profile(tree)` counts nodes per level
- `max_branching(tree)` returns maximum local width
- `is_squarefree(tree)` checks absence of recursive exponent nodes
- `leaf_ratio(tree)` compares leaves to nodes

None of these equals `support(P)`.

A future first-principles API alias issue may define `support(...)`, but that
should be done explicitly rather than inferred from existing metrics.

## Canonical vs extended boundary

`core.metrics_dict(tree)` is the current canonical metric dictionary.

`metrics.extended_metrics(tree)` adds research-facing values:

- `verticality_ratio`
- `structural_asymmetry`
- `subtree_mixing_score`
- `has_root_mixed_simple_pattern`

This boundary should remain explicit.

A metric should not become canonical merely because it appears in an extended
dictionary or because a CLI/reporting path uses it.

## Risks

### 1. Accidental promotion

Extended metrics can look stable because they are deterministic and simple.

Deterministic does not mean canonical.

Promotion into the canonical metric set should follow the admission rule in
`SPEC.md`.

### 2. Height confusion around `PET(1)`

`metrics.py` is tree-based and inherits `core.py`.

It should not be used as evidence that `PET(1)` has a standalone legacy tree
representation.

For `PET(1)`, the object-native bridge in `object_metrics.py` is the cleaner
semantic reference.

### 3. Support confusion

No existing metric in `metrics.py` is first-principles `support(P)`.

Support should remain current-level prime-root support, not a synonym for
branching, node count, profile width, or leaf behavior.

### 4. Research helper leakage

Functions using `pet.algebra._shape` are research-facing.

They should remain outside the stable PET-Base metric contract unless audited
and promoted explicitly.

## Recommendation

Do not change metric behavior in this issue.

Keep the current layering:

- `core.py` defines canonical PET-Base metrics
- `object_metrics.py` bridges legacy-compatible metrics to PETObject and `PET(1)`
- `metrics.py` provides extended metrics, derived classifiers, and research
  helpers

Before exposing first-principles API aliases such as `height(...)` or
`support(...)`, decide explicitly whether each alias targets:

- legacy PET-Base trees
- PETObject
- both through dispatch
- documentation only

## Known follow-up work

1. Decide first-principles API aliases in a separate design issue.
2. Classify CLI commands by stability level.
3. Add lightweight documentation consistency checks.
4. Review stale documentation references, including historical paths that no
   longer match the current `src/pet` package layout.

## Summary

`metrics.py` is useful, but it is not the canonical metric contract.

It is a derived and research-facing layer over canonical PET-Base metrics.

The most important semantic boundaries are:

- `height` is canonical for current `N >= 2` PET-Base trees in `core.py`
- `height(PET(1)) = 0` is cleanly represented in the object-native metric bridge
- `support(P)` is current-level prime-root support and is not implemented by
  existing extended metrics
- extended metrics should not be promoted into canonical output by accident
