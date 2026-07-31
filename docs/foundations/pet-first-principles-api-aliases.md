# PET first-principles API alias design

<!-- PETRA-HISTORICAL-FOUNDATION -->
> [!IMPORTANT]
> **Historical PET/PET-PEG design material.** This document does not define PETRA. Use [`../reference/SPEC.md`](../reference/SPEC.md) as the sole canonical specification.


This document defines the intended direction for explicit first-principles API
aliases.

The goal is semantic clarity, not implementation.

This document does not change implementation behavior.

## Background

The first-principles PET model defines conceptual operations such as:

- `PET(1)`
- `collapse(P)`
- `support(P)`
- `height(P)`

The current implementation has multiple layers:

- legacy PET-Base tree functions in `src/pet/core.py`
- PET/PEG object-native functions in `src/pet/object_model.py`
- PETObject metric helpers in `src/pet/object_metrics.py`
- extended and research metrics in `src/pet/metrics.py`
- public exports in `src/pet/__init__.py`

These layers are related, but they are not interchangeable.

## Current API situation

The public package currently exports `height` from `src/pet/core.py`.

That means:

    pet.height(tree)

currently means legacy PET-Base tree height.

It does not mean a universal first-principles height operation over every PET
representation.

This is important because `core.py` does not expose `PET(1)` as a standalone
tree object. It represents exponent leaf `1` implicitly with `None`.

The object-native layer, by contrast, supports:

    pet_object_from_int(1)

and the object metric bridge gives:

    pet_object_height(pet_object_from_int(1)) == 0

which matches the first-principles convention:

    height(PET(1)) = 0

## Design rule

Do not introduce ambiguous generic aliases.

In particular, do not add or rebind a generic public `height(...)` alias unless
the accepted input domain is explicit.

The name `height` is already public and currently belongs to the PET-Base tree
layer.

Changing or overloading that meaning would be a behavior and compatibility
change.

## Alias decision matrix

| Concept | First-principles meaning | Current closest implementation | Safe alias decision |
|---|---|---|---|
| `PET(1)` | recursive leaf object | `pet_object_from_int(1)` | Prefer object-native API. Do not force into legacy tree API. |
| `collapse(P)` | recursively evaluate a PET object to an integer | `decode(tree)` for legacy trees; `PETObject.value` for object-native objects | Do not expose generic `collapse(...)` until the input domain is explicit. |
| `support(P)` | current-level prime-root set | no direct public first-principles API | Design before implementation. Do not infer from `branch_profile`, `max_branching`, or `leaf_ratio`. |
| `height(P)` | recursive exponent-object height with `height(1) = 0` | `core.height(tree)` for `N >= 2` PET-Base trees; `pet_object_height(obj)` for PETObject including `PET(1)` | Do not rebind public `height`. Use explicit object/tree names if implemented. |
| canonical PET tree | compact PET-Base representation for `N >= 2` | `encode(n)`, `decode(tree)`, `validate(tree)` | Keep legacy tree API explicit. |
| canonical PET object | object-native representation for `n >= 1` | `pet_object_from_int(n)` | Keep object-native API explicit. |

## Recommended naming direction

If aliases are implemented later, prefer names that preserve representation
boundaries.

### Legacy PET-Base tree names

These names should remain tree-specific:

- `encode(n)`
- `decode(tree)`
- `height(tree)`
- `metrics_dict(tree)`
- `validate(tree)`

They target the compact PET-Base tree representation.

They should not be used to imply standalone first-principles support for
`PET(1)`.

### Object-native first-principles names

Potential future aliases should make the object domain explicit.

Candidate names:

- `pet_object_collapse(obj)`
- `pet_object_support(obj)`
- `pet_object_first_principles_height(obj)`

These names are verbose, but they avoid pretending that legacy trees and
PETObject are the same representation.

A shorter public alias can be considered later only after a dispatch policy is
defined.

## `collapse(...)`

Conceptually:

    collapse(P) = numeric value represented by P

For legacy PET-Base trees, the closest existing function is:

    decode(tree)

For PETObject, the represented integer value already exists on the object.

However, a generic `collapse(...)` function would need to answer:

1. Does it accept only `PETObject`?
2. Does it accept only legacy PET-Base trees?
3. Does it dispatch between both?
4. What does it do with invalid inputs?
5. Is it a public stable API or documentation terminology only?

Until those answers are explicit, `collapse(...)` should remain a documented
first-principles concept, not a new public alias.

## `support(...)`

Conceptually:

    support(P) = current-level prime roots of P

This is not the same as:

- `branch_profile(tree)`
- `max_branching(tree)`
- `node_count(tree)`
- `leaf_count(tree)`
- `leaf_ratio(tree)`
- `recursive_mass(tree)`

Support is current-level only.

It does not automatically include prime roots inside exponent objects.

A future implementation should avoid names such as recursive support unless a
separate recursive-support concept is explicitly defined.

## `height(...)`

First-principles height uses:

    height(1) = 0

and for compound PET objects:

    height(P) = 1 + max(height(E_i))

Legacy tree height in `core.py` is compatible for current `N >= 2` PET-Base
trees, but it does not define a standalone tree for `PET(1)`.

Therefore:

- `core.height(tree)` should remain legacy PET-Base tree height
- `pet_object_height(obj)` is currently the clean bridge for object-native height
- a future first-principles alias should not silently replace or overload
  public `height`

## Dispatch policy

A generic dispatching API could eventually accept both legacy trees and
PETObject instances.

That should be a separate implementation decision.

If dispatch is introduced, it must document:

- supported input types
- return types
- error behavior
- whether dispatch is stable API
- how `PET(1)` is represented
- whether legacy tree behavior remains unchanged

This issue does not implement dispatch.

## Compatibility boundary

Do not break existing users of:

    from pet import height

Today that import refers to `core.height`.

Any future first-principles API must avoid changing that meaning without a
separate compatibility decision.

## Recommendation

Do not implement API aliases in this issue.

Use this issue to record the design boundary:

- `collapse(P)` remains first-principles terminology for now
- `support(P)` remains current-level prime-root support
- `height(P)` remains conceptually first-principles, but public `height` already
  means legacy PET-Base tree height
- PETObject is the preferred representation for first-principles `PET(1)`
- legacy PET-Base tree APIs remain explicit and stable for `N >= 2`

## Follow-up implementation options

Possible future implementation paths:

1. Add object-explicit helpers only:
   - `pet_object_collapse(obj)`
   - `pet_object_support(obj)`
   - `pet_object_first_principles_height(obj)`

2. Add documentation-only aliases:
   - keep `collapse(P)`, `support(P)`, and `height(P)` as notation only

3. Add generic dispatching helpers:
   - `collapse(value)`
   - `support(value)`
   - `first_principles_height(value)`

4. Keep the current public API unchanged:
   - no new aliases
   - continue documenting first-principles concepts separately

Option 1 is the safest implementation path if code is added later.

Option 2 is the safest path for now.

## Known follow-up work

1. Decide whether API aliases should be implemented at all.
2. If implemented, decide whether aliases target PETObject only or dispatch
   across representations.
3. Add tests before exposing any public alias.
4. Update public exports only after compatibility review.
5. Keep stale documentation reference cleanup for the documentation consistency
   issue.

## Summary

First-principles names are useful, but ambiguous public aliases would make the
project less clear.

The safest current decision is documentation-only:

- do not change behavior
- do not rebind public `height`
- do not infer `support(P)` from existing metrics
- prefer PETObject for first-principles `PET(1)`
- keep legacy PET-Base tree APIs explicit
